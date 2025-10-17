import argparse
import os
import numpy as np
import json
import copy
import pickle
import time
import subprocess
import argparse

def load_relation_pairs(file_path, thershold):
    relation_pairs = set()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2:
                rel1, rel2, confidence = parts[0], parts[1], parts[2]
                if float(confidence) > thershold:
                    relation_pairs.add((rel1, rel2))
    return relation_pairs

def find_mutual_alignments(rel1_path, rel2_path, thershold):
    rel1_pairs = load_relation_pairs(rel1_path, thershold)
    rel2_pairs = load_relation_pairs(rel2_path, thershold)
    
    mutual_alignments = []
    rel2_to_rel1 = {}
    for rel1, rel2 in rel1_pairs:
        if rel2 not in rel2_to_rel1:
            rel2_to_rel1[rel2] = []
        rel2_to_rel1[rel2].append(rel1)
    
    for rel2, rel1 in rel2_pairs:
        if rel2 in rel2_to_rel1 and rel1 in rel2_to_rel1[rel2]:
            mutual_alignments.append((rel1, rel2))
    
    return mutual_alignments

# PARIS
def read_triples(file_path):
    """
    read relation / attribute triples from file
    :param file_path: relation / attribute triples file path
    :return: relation / attribute triples
    """
    triples = set()
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip('\n').split('\t')
            triples.add((line[0], line[1], line[2]))
    file.close()
    return triples

def turn_and_write(rel_triples, attr_triples, seeds_triples, out_path):
    file = open(out_path, 'w', encoding='utf-8')
    for (s, p, o) in rel_triples:
        file.write('<' + s + '> <' + p + '> <' + o + '> .\n')
    for (s, p, l) in seeds_triples:
        file.write('<' + s + '> <' + p + '> ' + l + ' .\n')
    file.close()


def seed_triples(data_dir):
    """
    Returns two lists of triples, with the seed for PARIS well formatted into
    ({resource}, {#label}, {label})
    Parameters
    ----------
    folder
    dataset_division
    fold_num

    Returns
    -------
    seed_triples_1
    seed_triples_2
    """
    seed_triples_1 = []
    seed_triples_2 = []
    with open(data_dir, encoding="utf-8") as f:
        for l in f:
            e1, e2 = l.strip("\n").split("\t")
            label = e1.split("/")[-1]

            label_str = '{resource} align "{label}"'

            # Add the label
            seed_triples_1.append((e1, "align", '"{}"'.format(label)))
            seed_triples_2.append((e2, "align", '"{}"'.format(label)))

    return seed_triples_1, seed_triples_2


    # 加入 KGC 预测出来的 .\pyclause_output\predicted_align.txt

def create_nt(dbp_train_file, fb_train_file, align_file, kg1: str, kg2: str):

    rel_triples_1 = read_triples(dbp_train_file)
    #attr_triples_1 = read_triples(folder + 'attr_triples_1')

    rel_triples_2 = read_triples(fb_train_file)
    #attr_triples_2 = read_triples(folder + 'attr_triples_2')

    attr_triples_1, attr_triples_2 = None, None
    seed_triples_1, seed_triples_2 = seed_triples(align_file)

    turn_and_write(rel_triples_1, attr_triples_1, seed_triples_1, kg1)
    turn_and_write(rel_triples_2, attr_triples_2, seed_triples_2, kg2)



def run_paris(out_folder, data_dir, ontology1, ontology2):
    current_time = time.localtime()
    ontology1 = os.path.abspath(ontology1)
    ontology2 = os.path.abspath(ontology2)

    name = data_dir.split('/')[-2]

    task_name = '%s_%02d%02d_%02d%02d%02d' % (name, current_time.tm_mon, current_time.tm_mday,
                                              current_time.tm_hour, current_time.tm_min, current_time.tm_sec)

    task_name = out_folder + task_name
    os.mkdir(task_name)
    os.mkdir('%s/output' % task_name)
    os.mkdir('%s/log' % task_name)

    with open(task_name + '/paris.ini', 'w', encoding="utf-8") as ini_file:
        ini_file.write('resultTSV = %s/output\n' % task_name)
        ini_file.write('factstore1 = %s\n' % ontology1)
        ini_file.write('factstore2 = %s\n' % ontology2)
        ini_file.write('home = %s/log\n' % task_name)

    _ = subprocess.call(['java', '-Xmx26000m', '-jar', './entity-matchers-new/paris.jar', task_name + '/paris.ini'])
    return task_name


def compute_prec_rec_f1(aligns, truth_links):
    """
    Note that aligns should have been pruned from the alignments already present in the
    seed.
    Truth link, hence, must contain only test and valid links.
    Parameters
    ----------
    aligns
    truth_links

    Returns
    -------

    """
    aligns = set(aligns)
    truth_links = set(truth_links)
    num_correct = len(aligns.intersection(truth_links))
    if num_correct == 0 or len(aligns) == 0:
        print("Got 0, 0, 0 in evaluation!!!")
        return 0, 0, 0
    precision = num_correct / len(aligns)
    recall = num_correct / len(truth_links)
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def evaluate_paris(paris_out_folder, data_dir, origin_dir, threshold, rel_threshold):
    run = 0
    res_list = []
    while True:
        full_path = paris_out_folder + "/output/{run}_eqv.tsv".format(run=run)
        if os.path.exists(full_path):
            # PARIS create an empty file at the last_iter+1. If we encountered it, we can break
            if os.stat(full_path).st_size == 0:
                break
        run += 1
    full_path = paris_out_folder + "/output/{run}_eqv_full.tsv".format(run=run - 1)
    # Get PARIS result from the .tsv and elaborate it a bit to be compared with the same_list
    with open(full_path, encoding="utf-8") as f:
        for l in f:
            (e1, e2, confidence) = l.split("\t")
            res_list.append((e1, e2, confidence))

    set_train = set()
    #with open(data_dir + "/aligned_entities.txt", encoding="utf-8") as f:
    with open(f"{origin_dir}/cross/known_shared_entities.txt", encoding="utf-8") as f:
        for l in f:
            (e1, e2) = l.rstrip("\n").split("\t")
            set_train.add((e1, e2))
    
    res_no_train = []
    filtered_res_list = []
    for align_with_confidence in res_list:
        align = (align_with_confidence[0], align_with_confidence[1])
        if align not in set_train:
            res_no_train.append(align)
            filtered_res_list.append(align_with_confidence)



    with open(data_dir + "/entity-matchers_output/predicted_align.txt", "w", encoding="utf-8") as f:
        for e1, e2, confidence in filtered_res_list:
            if float(confidence) > threshold:
                f.write(e1 + '\t' + e2 + '\n')


    relation1_dir = paris_out_folder + "/output/{run}_superrelations1.tsv".format(run=run - 1)
    relation2_dir = paris_out_folder + "/output/{run}_superrelations2.tsv".format(run=run - 1)
    
    mutual_alignments = find_mutual_alignments(relation1_dir, relation2_dir, rel_threshold)
    
    print("new align relation")
    with open(data_dir + "/entity-matchers_output/predicted_relation_align.txt", "w", encoding="utf-8") as f:
        for rel1, rel2 in mutual_alignments:
            print(f"{rel1} <-> {rel2}")
            f.write(f"{rel1}\t{rel2}\n")
    
    print(f"Found {len(mutual_alignments)} mutually aligned relation pairs")

    test_links = []
    valid_links = []



    with open(data_dir[:-2] + "/cross/test_shared_entities.txt", encoding="utf-8") as f:
        for l in f:
            (e1, e2) = l.rstrip("\n").split("\t")
            if (e1, e2) not in set_train:
                test_links.append((e1, e2))

    return compute_prec_rec_f1(res_no_train, test_links + valid_links)


def run_paris_experiment(data_dir, origin_dir, out_folder, threshold, rel_threshold, dbp_train_file, fb_train_file, align_file):
    precisions = []
    recalls = []
    f1s = []
    train_times = []
    test_times = []


    kg1_file = f"{data_dir}/entity-matchers_output/kg1.nt"
    kg2_file = f"{data_dir}/entity-matchers_output/kg2.nt"
    start_time = time.time()
    create_nt(dbp_train_file, fb_train_file, align_file, kg1_file, kg2_file)
    paris_out_folder = run_paris(out_folder, data_dir, kg1_file, kg2_file)
    train_time = time.time() - start_time
    start_time = time.time()
    precision, recall, f1 = evaluate_paris(paris_out_folder, data_dir, origin_dir, threshold, rel_threshold)
    test_time = time.time() - start_time

    precisions.append(precision)
    recalls.append(recall)
    f1s.append(f1)
    train_times.append(train_time)
    test_times.append(test_time)

    precisions = np.array(precisions)
    recalls = np.array(recalls)
    f1s = np.array(f1s)
    train_times = np.array(train_times)
    test_times = np.array(test_times)

    print("KGA results:")
    print("precisions: ", precisions)
    print("recalls: ", recalls)
    print("f1s: ", f1s)
    print("Train times: ", train_times)
    print("Test times: ", test_times)


    with open(f"./{data_dir}/entity-matchers_output/results.txt", "w", encoding="utf-8") as f:
        print("KGA results:", file=f)
        print("precisions: ", precisions, file=f)
        print("recalls: ", recalls, file=f)
        print("f1s: ", f1s, file=f)
        print("Train times: ", train_times, file=f)
        print("Test times: ", test_times, file=f)

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./data/CrossLPData/DBP-FB")
    parser.add_argument("--threshold", type=float, default=0)
    parser.add_argument("--rel_threshold", type=float, default=0)
    args = parser.parse_args()

    origin_dir = args.data_dir
    data_dir = args.data_dir
    d1, d2 = data_dir.split('/')[-1].split('-')
    run = 0
    while True:
        if not os.path.exists(data_dir + '/' + str(run)):
            break
        run += 1

    data_dir = data_dir + '/' + str(run-1)


    dbp_train_file = f"{origin_dir}/{d1}/train.txt"
    fb_train_file = f"{origin_dir}/{d2}/train.txt"
    align_file = f"{data_dir}/aligned_entities.txt"


    if not os.path.exists(f"{data_dir}/entity-matchers_output"):
        os.makedirs(f"{data_dir}/entity-matchers_output")
    out_folder = f"{data_dir}/entity-matchers_output/output"

    run_paris_experiment(data_dir, origin_dir, out_folder, args.threshold, args.rel_threshold, dbp_train_file, fb_train_file, align_file)