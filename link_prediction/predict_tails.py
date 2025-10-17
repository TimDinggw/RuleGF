from c_clause import QAHandler, Loader
from clause import Options
import sys, os
import argparse

def predict_tails(input_file_1, input_file_2 , output_file, data_dir, all_predicts, train_file, rules_file, threshold, bi_match):
    options = Options()
    
    options.set("qa_handler.collect_rules", False) 
    options.set("qa_handler.topk", 20) 
    options.set("qa_handler.verbose", False)
    
    loader = Loader(options=options.get("loader"))
    loader.load_data(data=train_file)
    loader.load_rules(rules=rules_file)
    
    qa_handler = QAHandler(options=options.get("qa_handler"))
    
    with open(input_file_1, "r", encoding="utf-8") as f:
        queries_1 = [line.strip().split("\t") for line in f if line.strip()]
    
    qa_handler.calculate_answers(queries=queries_1, loader=loader, direction="tail")
    
    answers_1_tail = qa_handler.get_answers(as_string=True)

    qa_handler.calculate_answers(queries=queries_1, loader=loader, direction="head")
    answers_1_head = qa_handler.get_answers(as_string=True)


    with open(input_file_2, "r", encoding="utf-8") as f:
        queries_2 = [line.strip().split("\t") for line in f if line.strip()]
    
    qa_handler.calculate_answers(queries=queries_2, loader=loader, direction="tail")
    
    answers_2_tail = qa_handler.get_answers(as_string=True)

    qa_handler.calculate_answers(queries=queries_2, loader=loader, direction="head")
    answers_2_head = qa_handler.get_answers(as_string=True)

    answers_1 = set()
    answers_2 = set()
    answers_all = set()

    with open(all_predicts, "w", encoding="utf-8") as f_out:
        for i, query in enumerate(queries_1):
            head, relation = query
            if len(answers_1_tail[i]):
                f_out.write(f"Query: {head}\t{relation}\n")
                for answer, confidence in answers_1_tail[i]:
                    f_out.write(f"\tPredicted Tail: {answer}\tConfidence: {confidence:.6f}\n")
                    if float(confidence) > threshold:
                        answers_1.add((head, answer))
                        answers_all.add((head, answer))
                        #break
                f_out.write("\n")
        f_out.write("-----------------------\n")
        for i, query in enumerate(queries_1):
            head, relation = query
            if len(answers_1_head[i]):
                f_out.write(f"Query: {head}\t{relation}\n")
                for answer, confidence in answers_1_head[i]:
                    f_out.write(f"\tPredicted Tail: {answer}\tConfidence: {confidence:.6f}\n")
                    if float(confidence) > threshold:
                        answers_1.add((head, answer))
                        answers_all.add((head, answer))
                        #break
                f_out.write("\n")
        f_out.write("-----------------------\n")
        for i, query in enumerate(queries_2):
            head, relation = query
            if len(answers_2_tail[i]):
                f_out.write(f"Query: {head}\t{relation}\n")
                for answer, confidence in answers_2_tail[i]:
                    f_out.write(f"\tPredicted Tail: {answer}\tConfidence: {confidence:.6f}\n")
                    if float(confidence) > threshold:
                        answers_2.add((answer, head))
                        answers_all.add((answer, head))
                        #break
                f_out.write("\n")
        f_out.write("-----------------------\n")
        for i, query in enumerate(queries_2):
            head, relation = query
            if len(answers_2_head[i]):
                f_out.write(f"Query: {head}\t{relation}\n")
                for answer, confidence in answers_2_head[i]:
                    f_out.write(f"\tPredicted Tail: {answer}\tConfidence: {confidence:.6f}\n")
                    if float(confidence) > threshold:
                        answers_2.add((answer, head))
                        answers_all.add((answer, head))
                        #break
                f_out.write("\n")
        f_out.write("-----------------------\n")
    
    answers = set()
    if  bi_match:
        answers = answers_1 & answers_2
    else:
        answers = answers_1 | answers_2

    answer = answers_all


    print("predict " + str(len(answers)) + " tails")
    with open(output_file, "w", encoding="utf-8") as f_out:
        if len(answers) == 0:
            f_out.write(f"xxx\tyyy\n")
        for e1, e2 in answers:
            f_out.write(f"{e1}\t{e2}\n")
    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="./data/CrossLPData/DBP-FB")
    parser.add_argument("--threshold", type=float, default=0)
    parser.add_argument("--bi_match", type=bool, default=False)
    args = parser.parse_args()

    origin_dir = args.data_dir
    data_dir = args.data_dir
    d1, d2 = args.data_dir.split('/')[-1].split('-')
    run = 0
    while True:
        if not os.path.exists(data_dir + '/' + str(run)):
            break
        run += 1

    data_dir = data_dir + '/' + str(run-1)
    #args.threshold = 0.1 * run

    all_entities_1 = set()
    all_entities_2 = set()
    with open(f"{origin_dir}/{d1}/train.txt", "r", encoding="utf-8") as f1, open(f"{origin_dir}/{d2}/train.txt", "r", encoding="utf-8") as f2:
        for line in f1.readlines():
            e1, r, e2 = line.strip('\n').split('\t')
            all_entities_1.add(e1)
            all_entities_1.add(e2)
        for line in f2.readlines():
            e1, r, e2 = line.strip('\n').split('\t')
            all_entities_2.add(e1)
            all_entities_2.add(e2)

    
    already_aligned_entities = set()
    #with open(f"{data_dir}/aligned_entities.txt", "r", encoding="utf-8") as f1:
    with open(f"{origin_dir}/cross/known_shared_entities.txt", "r", encoding="utf-8") as f1:
        for line in f1.readlines():
            e1, e2 = line.strip('\n').split('\t')
            already_aligned_entities.add(e1)
            already_aligned_entities.add(e2)

    train_file = f"{data_dir}/pyclause_output/train-align.txt"
    rules_file = f"{data_dir}/pyclause_output/rules_to_predict.txt"

    input_file_1 = f"{data_dir}/pyclause_output/to_predicted_align_1.txt"
    input_file_2 = f"{data_dir}/pyclause_output/to_predicted_align_2.txt"
    all_predicts = f"{data_dir}/pyclause_output/all_predicts.txt"
    output_file = f"{data_dir}/pyclause_output/predicted_align.txt"
    
    with open(input_file_1, "w", encoding="utf-8") as f:
        for e in all_entities_1:
            #if not e in already_aligned_entities:
            f.write(e + '\talign\n')
    with open(input_file_2, "w", encoding="utf-8") as f:
        for e in all_entities_2:
            #if not e in already_aligned_entities:
            f.write(e + '\talign\n')

    
    predict_tails(input_file_1, input_file_2 , output_file, data_dir, all_predicts, train_file, rules_file, args.threshold, args.bi_match)
    print(f"Predictions written to {output_file}")