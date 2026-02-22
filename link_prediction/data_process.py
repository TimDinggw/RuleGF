import shutil, os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, default="./data/CrossLPData/DBP-FB")
args = parser.parse_args()

data_dir = args.data_dir
origin_dir = args.data_dir

run = 0
while True:
    if not os.path.exists(args.data_dir + '/' + str(run)):
        break
    run += 1


if run == 0:
    d1, d2 = origin_dir.split('/')[-1].split('-')
    data_dir = origin_dir + '/0'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


    align_pairs = dict()
    with open(f"{origin_dir}/cross/known_shared_entities.txt", "r", encoding="utf-8") as f1, open(f"{data_dir}/aligned_entities.txt", "w", encoding="utf-8") as f2:
        lines = f1.readlines()
        f2.writelines(lines) 
        for line in lines:
            e1, e2 = line.strip().split('\t')
            align_pairs[e2] = e1

    splits = ['train', 'test', 'valid']
    for split in splits:
        with open(f"{origin_dir}/{d1}/{split}.txt", "r", encoding="utf-8") as f1, open(f"{origin_dir}/{d2}/{split}.txt", "r", encoding="utf-8") as f2, open(f"{data_dir}/{split}.txt", "w", encoding="utf-8") as f3:
            f3.writelines(f1.readlines())
            for line in f2.readlines():
                h, r, t = line.strip().split('\t')
                if h in align_pairs.keys():
                    h = align_pairs[h]
                if t in align_pairs.keys():
                    t = align_pairs[t]
                f3.write(f"{h}\t{r}\t{t}\n")

    for d in [d1]:
        source_folder = f"{origin_dir}/{d}"
        destination_folder = f"{data_dir}/{d}"
        shutil.copytree(source_folder, destination_folder)

    if not os.path.exists(f"{data_dir}/{d2}"):
        os.makedirs(f"{data_dir}/{d2}")
    for split in splits:
        with open(f"{origin_dir}/{d2}/{split}.txt", "r", encoding="utf-8") as f1, open(f"{data_dir}/{d2}/{split}.txt", "w", encoding="utf-8") as f2:
            for line in f1.readlines():
                h, r, t = line.strip().split('\t')
                if h in align_pairs.keys():
                    h = align_pairs[h]
                if t in align_pairs.keys():
                    t = align_pairs[t]
                f2.write(f"{h}\t{r}\t{t}\n")
       

    with open(f"{data_dir}/cross_train.txt", "w", encoding="utf-8") as f1, open(f"{origin_dir}/{d1}/train.txt", "r", encoding="utf-8") as f2, open(f"{origin_dir}/{d2}/train.txt", "r", encoding="utf-8") as f3:
        f1.writelines(f2.readlines())
        for line in f3.readlines():
            h, r, t = line.strip().split('\t')
            if h in align_pairs.keys():
                h = align_pairs[h]
            if t in align_pairs.keys():
                t = align_pairs[t]
            f1.write(f"{h}\t{r}\t{t}\n")
       

    with open(f"{data_dir}/cross_test.txt", "w", encoding="utf-8") as f1, open(f"{origin_dir}/cross/cross_test.txt", "r", encoding="utf-8") as f2:
        for line in f2.readlines():
            h, r, t = line.strip().split('\t')
            if h in align_pairs.keys():
                h = align_pairs[h]
            if t in align_pairs.keys():
                t = align_pairs[t]
            f1.write(h+'\t'+r+'\t'+t+'\n')
        
    # with open(f"{data_dir}/cross_test_distinct_entity.txt", "w", encoding="utf-8") as f1, open(f"{origin_dir}/cross/cross_test_distinct_entity.txt", "r", encoding="utf-8") as f2:
    #     for line in f2.readlines():
    #         h, r, t = line.strip().split('\t')
    #         if h in align_pairs.keys():
    #             h = align_pairs[h]
    #         if t in align_pairs.keys():
    #             t = align_pairs[t]
    #         f1.write(h+'\t'+r+'\t'+t+'\n')

    # with open(f"{data_dir}/cross_test_distinct_relation.txt", "w", encoding="utf-8") as f1, open(f"{origin_dir}/cross/cross_test_distinct_relation.txt", "r", encoding="utf-8") as f2:
    #     for line in f2.readlines():
    #         h, r, t = line.strip().split('\t')
    #         if h in align_pairs.keys():
    #             h = align_pairs[h]
    #         if t in align_pairs.keys():
    #             t = align_pairs[t]
    #         f1.write(h+'\t'+r+'\t'+t+'\n')
else:
    data_dir_pre = args.data_dir + '/' + str(run-2)
    data_dir = args.data_dir + '/' + str(run-1)

    d1, d2 = origin_dir.split('/')[-1].split('-')



    align_pairs = dict()
    with open(f"{data_dir_pre}/aligned_entities.txt", "r", encoding="utf-8") as f1:
        for line in f1.readlines():
            e1, e2 = line.strip().split('\t')
            align_pairs[e2] = e1

    splits = ['test', 'valid']

    for split in splits:
        # for d in [d1, d2]:
        for d in [d1]:
            source_folder = f"{args.data_dir}/{d}/{split}.txt"
            destination_folder = f"{data_dir}/{d}/{split}.txt"
            shutil.copy(source_folder, destination_folder)

        with open(f"{args.data_dir}/{d2}/{split}.txt", "r", encoding="utf-8") as f1, open(f"{data_dir}/{d2}/{split}.txt", "w", encoding="utf-8") as f2:
                for line in f1.readlines():
                    h, r, t = line.strip().split('\t')
                    if h in align_pairs.keys():
                        h = align_pairs[h]
                    if t in align_pairs.keys():
                        t = align_pairs[t]
                    f2.write(f"{h}\t{r}\t{t}\n")




    for split in splits:
        with open(f"{args.data_dir}/{d1}/{split}.txt", "r", encoding="utf-8") as f1, open(f"{args.data_dir}/{d2}/{split}.txt", "r", encoding="utf-8") as f2, open(f"{data_dir}/{split}.txt", "w", encoding="utf-8") as f3:
            # lines = f1.readlines() + f2.readlines()
            # f3.writelines(lines)
            f3.writelines(f1.readlines())
            for line in f2.readlines():
                h, r, t = line.strip().split('\t')
                if h in align_pairs.keys():
                    h = align_pairs[h]
                if t in align_pairs.keys():
                    t = align_pairs[t]
                f3.write(f"{h}\t{r}\t{t}\n")


    splits = ['train']
    for split in splits:
        with open(f"{data_dir}/{d1}/{split}.txt", "r", encoding="utf-8") as f1, open(f"{data_dir}/{d2}/{split}.txt", "r", encoding="utf-8") as f2, open(f"{data_dir}/{split}.txt", "w", encoding="utf-8") as f3:
            # lines = f1.readlines() + f2.readlines()
            # f3.writelines(lines)
            f3.writelines(f1.readlines())
            for line in f2.readlines():
                h, r, t = line.strip().split('\t')
                if h in align_pairs.keys():
                    h = align_pairs[h]
                if t in align_pairs.keys():
                    t = align_pairs[t]
                f3.write(f"{h}\t{r}\t{t}\n")

    # with open(f"{args.data_dir}/cross/known_shared_entities.txt", "r", encoding="utf-8") as f1, open(f"{data_dir}/aligned_entities.txt", "w", encoding="utf-8") as f3:
    #         lines = f1.readlines()
    #         f3.writelines(lines)



    with open(f"{data_dir}/cross_train.txt", "w", encoding="utf-8") as f1, open(f"{origin_dir}/{d1}/train.txt", "r", encoding="utf-8") as f2, open(f"{origin_dir}/{d2}/train.txt", "r", encoding="utf-8") as f3:
        f1.writelines(f2.readlines())
        for line in f3.readlines():
            h, r, t = line.strip().split('\t')
            if h in align_pairs.keys():
                h = align_pairs[h]
            if t in align_pairs.keys():
                t = align_pairs[t]
            f1.write(f"{h}\t{r}\t{t}\n")
       

    with open(f"{data_dir}/cross_test.txt", "w", encoding="utf-8") as f1, open(f"{origin_dir}/cross/cross_test.txt", "r", encoding="utf-8") as f2:
        for line in f2.readlines():
            h, r, t = line.strip().split('\t')
            if h in align_pairs.keys():
                h = align_pairs[h]
            if t in align_pairs.keys():
                t = align_pairs[t]
            f1.write(h+'\t'+r+'\t'+t+'\n')
        
    # with open(f"{data_dir}/cross_test_distinct_entity.txt", "w", encoding="utf-8") as f1, open(f"{origin_dir}/cross/cross_test_distinct_entity.txt", "r", encoding="utf-8") as f2:
    #     for line in f2.readlines():
    #         h, r, t = line.strip().split('\t')
    #         if h in align_pairs.keys():
    #             h = align_pairs[h]
    #         if t in align_pairs.keys():
    #             t = align_pairs[t]
    #         f1.write(h+'\t'+r+'\t'+t+'\n')

    # with open(f"{data_dir}/cross_test_distinct_relation.txt", "w", encoding="utf-8") as f1, open(f"{origin_dir}/cross/cross_test_distinct_relation.txt", "r", encoding="utf-8") as f2:
    #     for line in f2.readlines():
    #         h, r, t = line.strip().split('\t')
    #         if h in align_pairs.keys():
    #             h = align_pairs[h]
    #         if t in align_pairs.keys():
    #             t = align_pairs[t]
    #         f1.write(h+'\t'+r+'\t'+t+'\n')
