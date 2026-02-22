from clause import Learner, Options
from clause.util.utils import get_base_dir
from c_clause import Loader
import os
import argparse

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


if not os.path.exists(f"{data_dir}/pyclause_output"):
    os.makedirs(f"{data_dir}/pyclause_output")

path_train = f"./{data_dir}/cross_train.txt"
path_rules_output = f"./{data_dir}/pyclause_output/cross-rules.txt"



# load custom config from file
#options = Options(f"{get_base_dir()}/config-my.yaml")
options = Options("./link_prediction/config-my.yaml")

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
options.set("learner.anyburl.time", 120)
options.set("learner.anyburl.raw.MAX_LENGTH_CYCLIC", 5)#5
options.set("learner.anyburl.raw.WORKER_THREADS", 10)
# you can also add java vm params like so: 
options.set("learner.anyburl.java_options", ["-Dfile.encoding=UTF-8"])

learner = Learner(options=options.get("learner"))
learner.learn_rules(path_data=path_train, path_output=path_rules_output)

# directly load the rules into c_clause
options.set("loader.c_max_length", 5)#4

loader = Loader(options.get("loader"))
loader.load_data(data=path_train)
loader.load_rules(rules=path_rules_output)
