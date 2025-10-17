from c_clause import RankingHandler, Loader
from clause.util.utils import get_base_dir
from clause import Options

from clause import Ranking
from clause import TripleSet

import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, default="./data/CrossLPData/DBP-FB")
args = parser.parse_args()

data_dir = args.data_dir

run = 0
while True:
    if not os.path.exists(data_dir + '/' + str(run)):
        break
    run += 1

data_dir = data_dir + '/' + str(run-1)


train = f"{data_dir}/train.txt"
filter_set = f"{data_dir}/valid.txt"


with open(f"{data_dir}/train.txt", "r", encoding="utf-8") as f1, open(f"{data_dir}/valid.txt", "r", encoding="utf-8") as f2, open(f"{data_dir}/filterset.txt", "w", encoding="utf-8") as f3: 
    f3.writelines(f1.readlines() + f2.readlines())
filter_set = f"{data_dir}/filterset.txt"

target = f"{data_dir}/test.txt"
rules = f"{data_dir}/pyclause_output/rules.txt"
ranking_file = f"{data_dir}/pyclause_output/ranking.txt"


options = Options()
options.set("ranking_handler.aggregation_function", "maxplus")
options.set("ranking_handler.topk", 200)
options.set("loader.load_u_d_rules", True)
options.set("loader.load_u_xxc_rules", False)
options.set("loader.load_u_xxd_rules", False)
options.set("ranking_handler.num_threads", 64)

#### Calculate a ranking
loader = Loader(options=options.get("loader"))
loader.load_data(data=train, filter=filter_set, target=target)
loader.load_rules(rules=rules)

ranker = RankingHandler(options=options.get("ranking_handler"))
ranker.calculate_ranking(loader=loader)
headRanking = ranker.get_ranking(direction="head", as_string=True)
tailRanking = ranker.get_ranking(direction="tail", as_string=True)

testset = TripleSet(target, encod="utf-8")
ranking = Ranking(k=200)

# process the handler ranking which is defined on queries and not
# on triples, e.g. assign to every triple of 'testset' the corresponding query rankings
ranking.convert_handler_ranking(headRanking, tailRanking, testset)
ranking.compute_scores(testset.triples)


# print("*** EVALUATION RESULTS ****")
print("KGC results:")
print("Num triples: " + str(len(testset.triples)))
print("MRR     " + '{0:.6f}'.format(ranking.hits.get_mrr()))
print("hits@1  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(1)))
print("hits@3  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(3)))
print("hits@5  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(5)))
print("hits@10 " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(10)))
print()

# now some code to some nice overview on the different relations and directions
# the loop interates over all relations in the test set
print("relation".ljust(25) + "\t" + "MRR-h" + "\t" + "MRR-t" + "\t" + "Num triples")


with open(f"./{data_dir}/pyclause_output/results.txt", "w", encoding="utf-8") as f:
   # 写入评估结果
   #print("*** EVALUATION RESULTS ****", file=f)
   print("KGC results:", file=f)
   print("Num triples: " + str(len(testset.triples)), file=f)
   print("MRR     " + '{0:.6f}'.format(ranking.hits.get_mrr()), file=f)
   print("hits@1  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(1)), file=f)
   print("hits@3  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(3)), file=f)
   print("hits@5  " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(5)), file=f)
   print("hits@10 " + '{0:.6f}'.format(ranking.hits.get_hits_at_k(10)), file=f)
   print(file=f)
   print("relation".ljust(25) + "\t" + "MRR-h" + "\t" + "MRR-t" + "\t" + "Num triples", file=f)

   for rel in testset.rels:
      rel_token = testset.index.id2to[rel]
      # store all triples that use the current relation rel in rtriples
      rtriples = list(filter(lambda x: x.rel == rel, testset.triples))

      # compute scores in head direction ...
      ranking.compute_scores(rtriples, True, False)
      (mrr_head, h1_head) = (ranking.hits.get_mrr(), ranking.hits.get_hits_at_k(1))
      # ... and in tail direction
      ranking.compute_scores(rtriples, False, True)
      (mrr_tail, h1_tail) = (ranking.hits.get_mrr(), ranking.hits.get_hits_at_k(1))
      # print the resulting scores
      print(rel_token.ljust(25) +  "\t" + '{0:.3f}'.format(mrr_head) + "\t" + '{0:.3f}'.format(mrr_tail) + "\t" + str(len(rtriples)))
      print(rel_token.ljust(25) + "\t" + '{0:.3f}'.format(mrr_head) + "\t" + '{0:.3f}'.format(mrr_tail) + "\t" + str(len(rtriples)), file=f)


# finally, write the ranking to a file, there are two ways to to this, both reults into the same ranking
ranker.write_ranking(path=ranking_file, loader=loader)
