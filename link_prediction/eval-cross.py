from c_clause import RankingHandler, Loader, PredictionHandler
from clause import Options, Ranking, TripleSet
import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, default="./data/CrossLPData/DBP-FB")
args = parser.parse_args()

data_dir = args.data_dir
origin_data = args.data_dir
run = 0
while True:
    if not os.path.exists(data_dir + '/' + str(run)):
        break
    run += 1
data_dir = data_dir + '/' + str(run-1)


train = f"{data_dir}/cross_train.txt"
filter_set = f"{data_dir}/valid.txt"

with open(f"{data_dir}/cross_train.txt", "r", encoding="utf-8") as f1, open(f"{data_dir}/valid.txt", "r", encoding="utf-8") as f2, open(f"{data_dir}/filterset.txt", "w", encoding="utf-8") as f3: 
    f3.writelines(f1.readlines() + f2.readlines())
filter_set = f"{data_dir}/filterset.txt"

target = f"{data_dir}/cross_test.txt"
target1 = f"{data_dir}/cross_test_distinct_entity.txt"  # target1
target2 = f"{data_dir}/cross_test_distinct_relation.txt"  # target2

rules = f"{data_dir}/pyclause_output/cross-rules.txt"
ranking_file = f"{data_dir}/pyclause_output/cross-ranking.txt"
explanations_file = f"{data_dir}/pyclause_output/cross-explanations.txt"


options = Options()
options.set("ranking_handler.aggregation_function", "maxplus")
options.set("ranking_handler.topk", 200)
options.set("loader.load_u_d_rules", True)
options.set("loader.load_u_xxc_rules", False)
options.set("loader.load_u_xxd_rules", False)
options.set("ranking_handler.num_threads", 64)

def evaluate_target(target_path, target_name):
    loader = Loader(options=options.get("loader"))
    loader.load_data(data=train, filter=filter_set, target=target_path)
    loader.load_rules(rules=rules)
    

    ranker = RankingHandler(options=options.get("ranking_handler"))
    ranker.calculate_ranking(loader=loader)
    head_ranking = ranker.get_ranking(direction="head", as_string=True)
    tail_ranking = ranker.get_ranking(direction="tail", as_string=True)
    
    testset = TripleSet(target_path, encod="utf-8")
    ranking = Ranking(k=200)
    ranking.convert_handler_ranking(head_ranking, tail_ranking, testset)
    ranking.compute_scores(testset.triples)
    
    print(f"\n*** {target_name} EVALUATION RESULTS ****")
    print("Num triples: " + str(len(testset.triples)))
    print("MRR     " + '{0:.6f}'.format(ranking.hits.get_mrr()))
    print("hits@1  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(1)))
    print("hits@3  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(3)))
    print("hits@5  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(5)))
    print("hits@10 " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(10)))
    
    with open(f"{data_dir}/pyclause_output/cross-results.txt", "a", encoding="utf-8") as f:
        f.write(f"\n*** {target_name} EVALUATION RESULTS ****\n")
        f.write("Num triples: " + str(len(testset.triples)) + "\n")
        f.write("MRR     " + '{0:.6f}'.format(ranking.hits.get_mrr()) + "\n")
        f.write("hits@1  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(1)) + "\n")
        f.write("hits@3  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(3)) + "\n")
        f.write("hits@5  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(5)) + "\n")
        f.write("hits@10 " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(10)) + "\n")

    # for case study
    # if "ALL" in target_name:
    #     options.set("prediction_handler.collect_explanations", True)
    #     scorer = PredictionHandler(options=options.get("prediction_handler"))
        
    #     scorer.calculate_scores(triples=target_path, loader=loader)
    #     scorer.write_explanations(path=f"{data_dir}/pyclause_output/my-exp.txt", as_string=True)

    if "ALL" in target_name:
        ranker.write_ranking(path=ranking_file, loader=loader)

    return ranking, testset

ranking, testset = evaluate_target(target, "ALL TEST SET")
ranking1, testset1 = evaluate_target(target1, "DISTINCT ENTITY TEST SET")
ranking2, testset2 = evaluate_target(target2, "DISTINCT RELATION TEST SET")
