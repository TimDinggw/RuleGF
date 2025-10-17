import os
from collections import defaultdict
import argparse

def load_triples(file_path):
    triples = list()
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            h, r, t = line.strip().split('\t')
            triples.append((h, r, t))
    return triples

def load_align_pairs(out_dir, align_file0, align_file1, align_file2, mode):
    align_pairs1 = dict()
    align_pairs2 = dict()
    align0 = set()
    align1 = set()
    align2 = set()

    with open(align_file1, 'r', encoding='utf-8') as f:
        for line in f:
            e1, e2 = line.strip().split('\t')
            align1.add((e1, e2))

    with open(align_file2, 'r', encoding='utf-8') as f:
        for line in f:
            e1, e2 = line.strip().split('\t')
            align2.add((e1, e2))
    with open(align_file0, 'r', encoding='utf-8') as f:
        for line in f:
            e1, e2 = line.strip().split('\t')
            align0.add((e1, e2))

    if mode == "noKGC":
        e_in_align2 = set()
        for e1, e2 in align0:
            e_in_align2.add(e1)
            e_in_align2.add(e2)
        align = set()
        align.update(align0)
        for e1, e2 in align2:
            if e1 not in e_in_align2 and e2 not in e_in_align2:
                align.add((e1, e2))
    elif mode == "noCR":
        align = align0 | (align1 & align2)
    elif mode == "noboth":
        align = align0 | align2
    else:
        e_in_align2 = set()
        for e1, e2 in align0:
            e_in_align2.add(e1)
            e_in_align2.add(e2)
        align = set()
        align.update(align0)
        for e1, e2 in (align1 & align2):
            if e1 not in e_in_align2 and e2 not in e_in_align2:
                align.add((e1, e2))

    for e1, e2 in align:
        align_pairs1[e1] = e2
        align_pairs2[e2] = e1
  
    print("len(align) ", len(align0), " + ", len(align) - len(align0), " = ", len(align))
    with open(f"{out_dir}/aligned_entities.txt", "w", encoding='utf-8') as f:
        for e1, e2 in align:
            f.write(e1 + '\t' + e2 + '\n')

    print("new align entity")
    with open(f"{out_dir}/new_aligned_entities.txt", "w", encoding='utf-8') as f:
        for (e1, e2) in align:
            if (e1, e2) not in align0:
                f.write(e1 + '\t' + e2 + '\n')
                #print(f"{e1} {e2}")

    return align_pairs1, align_pairs2

def load_relation_align_pairs(align_file0):
    align_pairs1 = dict()
    align_pairs2 = dict()
    with open(align_file0, 'r', encoding='utf-8') as f:
        for line in f:
            e1, e2 = line.strip().split('\t')
            align_pairs1[e1] = e2
            align_pairs2[e2] = e1

            # align_pairs1[e2] = e1
            # align_pairs2[e1] = e2

    #return align_pairs1, align_pairs1
    return align_pairs1, align_pairs2

def expand_triples(source_triples, target_triples, align_pairs, relation_align_pairs):
    # if target_triples is None:
    #     target_triples = set()
    
    # expanded_triples = set(target_triples)


    ent2rel = dict()
    relation_align_pairs_rules = set()
    
    for h, r, t in source_triples:
        # if (h, t) in ent2rel.keys():
        #     print("already have : ", h, r, t, ent2rel[(h, t)])
        if (h, t) not in ent2rel.keys():
            ent2rel[(h, t)] = [r]
        else:
            ent2rel[(h, t)].append(r)
        
    for h, r, t in target_triples:
        if h in align_pairs.keys() and t in align_pairs.keys():
            new_h = align_pairs[h]
            new_t = align_pairs[t]
            if (new_h, new_t) in ent2rel.keys() and len(ent2rel[(new_h, new_t)]) == 1:
                for new_r in ent2rel[(new_h, new_t)]:
                    relation_align_pairs_rules.add((r, new_r))

    relation_align_pairs = dict(relation_align_pairs.items() & relation_align_pairs_rules)
    #relation_align_pairs = dict(relation_align_pairs_rules)
    for x, y in relation_align_pairs.items():
        print(x, y)

    expanded_triples = set(source_triples)
    expanded_triples_new = set()

    return expanded_triples, expanded_triples_new


    for h, r, t in target_triples:
        if h in align_pairs.keys() and t in align_pairs.keys() and r in relation_align_pairs.keys():
            new_h = align_pairs[h]
            new_t = align_pairs[t]
            new_r = relation_align_pairs[r]
            if '-' in new_r:
                new_r = new_r[:-1]
                if (new_t, new_r, new_h) not in expanded_triples:
                    expanded_triples_new.add((new_t, new_r, new_h))
            else:
                if (new_h, new_r, new_t) not in expanded_triples:
                    expanded_triples_new.add((new_h, new_r, new_t))

    expanded_triples.update(expanded_triples_new)
    return list(expanded_triples), list(expanded_triples_new)

def save_triples(triples, file_path):
    with open(file_path, 'w', encoding='utf-8') as f:
        for h, r, t in triples:
            f.write(f"{h}\t{r}\t{t}\n")
    
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./data/CrossLPData/DBP-FB")
    parser.add_argument("--ablation", type=str, default="default")
    args = parser.parse_args()

    origin_dir = args.data_dir
    data_dir = args.data_dir
    d1, d2 = data_dir.split('/')[-1].split('-')
    run = 0
    while True:
        if not os.path.exists(data_dir + '/' + str(run)):
            break
        run += 1

    data_dir = args.data_dir + '/' + str(run-1)


    dbp_train_file = f"{origin_dir}/{d1}/train.txt"
    fb_train_file = f"{origin_dir}/{d2}/train.txt"
    align_file0 = f"{data_dir}/aligned_entities.txt"
    
    align_file1 = f"{data_dir}/pyclause_output/predicted_align.txt"
    align_file2 = f"{data_dir}/entity-matchers_output/predicted_align.txt"
    relation_align_file = f"{data_dir}/entity-matchers_output/predicted_relation_align.txt"
    
    out_dir = args.data_dir + '/' + str(run)
    output_dbp_dir = f"{out_dir}/{d1}"
    output_fb_dir = f"{out_dir}/{d2}"
    
    os.makedirs(output_dbp_dir, exist_ok=True)
    os.makedirs(output_fb_dir, exist_ok=True)
    
    align_pairs1, align_pairs2 = load_align_pairs(out_dir, align_file0, align_file1, align_file2, args.ablation)
    relation_align_pairs1, relation_align_pairs2 = load_relation_align_pairs(relation_align_file)

    dbp_train_triples = load_triples(dbp_train_file)
    fb_train_triples = load_triples(fb_train_file)

    expanded_dbp_triples, expanded_dbp_triples_new = expand_triples(dbp_train_triples, fb_train_triples, align_pairs2, relation_align_pairs2)
    
    expanded_fb_triples, expanded_fb_triples_new = expand_triples(fb_train_triples, dbp_train_triples, align_pairs1, relation_align_pairs1)
    with open(f"{data_dir}/expand_triples.txt", "w", encoding="utf-8") as f:
        for h, r, t in list(expanded_dbp_triples_new) + list(expanded_fb_triples_new):
            f.write(h+'\t'+r+'\t'+t+'\n')
    save_triples(expanded_dbp_triples, f"{output_dbp_dir}/train.txt")
    save_triples(expanded_fb_triples, f"{output_fb_dir}/train.txt")
    print(f"DBP: {len(dbp_train_triples)} + {len(expanded_dbp_triples) - len(dbp_train_triples)} = {len(expanded_dbp_triples)}")
    print(f"FB : {len(fb_train_triples)} + {len(expanded_fb_triples) - len(fb_train_triples)} = {len(expanded_fb_triples)}")
    