from clause import Learner, Options
from clause.util.utils import get_base_dir
from c_clause import Loader
import os
import argparse

# *** Example for rule learning with AnyBURL or Amie  ***

#path_train = f"{get_base_dir()}/data/wnrr/train.txt"
#path_rules_output = f"{get_base_dir()}/local/myrules/rules-wn18rr.txt"

# run = 0
# while True:
#     data_dir = "./data/CrossLPData/DBP-FB/{run}".format(run=run)
#     print(data_dir)
#     if not os.path.exists(data_dir):
#         # PARIS create an empty file at the last_iter+1. If we encountered it, we can break
#         #if os.stat(full_path).st_size == 0:
#         break
#     run += 1

# data_dir = "./data/CrossLPData/DBP-FB/{run}".format(run=run-1)

parser = argparse.ArgumentParser()
parser.add_argument("--data_dir", type=str, default="./data/CrossLPData/DBP-FB")
args = parser.parse_args()


data_dir = args.data_dir


run = 0
while True:
    if not os.path.exists(data_dir + '/' + str(run)):
        # PARIS create an empty file at the last_iter+1. If we encountered it, we can break
        #if os.stat(full_path).st_size == 0:
        break
    run += 1

data_dir = data_dir + '/' + str(run-1)




# path_train = f"../data/{data_dir}/train.txt"
# path_rules_output = f"../local/myrules/rules-{data_dir}.txt"

if not os.path.exists(f"{data_dir}/pyclause_output"):
    os.makedirs(f"{data_dir}/pyclause_output")

# with open(f"./{data_dir}/train.txt", "r", encoding="utf-8") as f1, open(f"./{data_dir}/aligned_entities.txt", "r", encoding="utf-8") as f2, open(f"./{data_dir}/pyclause_output/train-align.txt", "w", encoding="utf-8") as f3:
#     f3.writelines(f1.readlines())
#     for line in f2.readlines():
#         t = line.strip('\n').split('\t')
#         f3.write(t[0] + '\talign\t' + t[1] + '\n')
#         f3.write(t[1] + '\talign\t' + t[0] + '\n')
        
path_train = f"./{data_dir}/train.txt"
path_rules_output = f"./{data_dir}/pyclause_output/rules.txt"




# with open(f"../data/{data_dir}/train.txt", "r", encoding="utf-8") as f1, open(f"../data/{data_dir}/known_shared_entities.txt", "r", encoding="utf-8") as f2, open(f"../data/{data_dir}/train-align+self.txt", "w", encoding="utf-8") as f3:
#     ent_names = set()
#     for line in f1.readlines():
#         f3.write(line)
#         t = line.strip('\n').split('\t')
#         ent_names.add(t[0])
#         ent_names.add(t[2])
#     for line in f2.readlines():
#         t = line.strip('\n').split('\t')
#         f3.write(t[0] + '\talign\t' + t[1] + '\n')
#         f3.write(t[1] + '\talign\t' + t[0] + '\n')
#     for ent_name in ent_names:
#         f3.write(ent_name + '\talign\t' + ent_name + '\n')

# path_train = f"../data/{data_dir}/train-align+self.txt"
# path_rules_output = f"../local/myrules/rules-{data_dir}-align+self.txt"















# load custom config from file
#options = Options(f"{get_base_dir()}/config-my.yaml")
options = Options("./PyClause-new-1/config-my.yaml")

# set "amie" or "anyburl" and define specifc arguments
# AMIE
# options.set("learner.mode", "amie")
# # we are choosing a parameter setting here, which works well for the KBC scenario
# options.set("learner.amie.raw.maxad", 4)
# options.set("learner.amie.raw.minc", 0.0001)
# options.set("learner.amie.raw.minpca", 0.0001)
# options.set("learner.amie.raw.minhc", 0.0001)
# options.set("learner.amie.raw.mins", 2)
# options.set("learner.amie.raw.const", "*flag*") # special syntax for enforcing -const to be used as flag without value
# options.set("learner.amie.raw.maxadc", 2)
# # you can also add java vm params like so: 
# options.set("learner.amie.java_options", ["-Dfile.encoding=UTF-8"])

# rule learning with AnyBURL works similar

options.set("learner.mode", "anyburl")
options.set("learner.anyburl.time", 120)#60
options.set("learner.anyburl.raw.MAX_LENGTH_CYCLIC", 5)#5
options.set("learner.anyburl.raw.WORKER_THREADS", 10)
# you can also add java vm params like so: 
options.set("learner.anyburl.java_options", ["-Dfile.encoding=UTF-8"])

learner = Learner(options=options.get("learner"))
learner.learn_rules(path_data=path_train, path_output=path_rules_output)

# directly load the rules into c_clause
options.set("loader.c_max_length", 5)

loader = Loader(options.get("loader"))
loader.load_data(data=path_train)
loader.load_rules(rules=path_rules_output)

