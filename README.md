
# RuleGF: Rule-Guided Graph Fusion for Link Prediction across Knowledge Graphs

## Installation
Install Python and [PyClause](https://github.com/symbolic-kg/PyClause)
- python=3.9.12
- pyclause=0.0.1

## Training and Evaluation

### Datasets
We use the following datasets for training and evaluation:
- ​**​DBP-FB​**​ (DBpedia-Freebase)
- ​**​WIKI-YAGO​**​ (Wikidata-YAGO3)

These datasets are available from:
- [CLP GitHub repository](https://github.com/nju-websoft/CLP)
- [Hugging Face Datasets](https://huggingface.co/datasets/yncui-nju/CrossLPData)(direct download)

### Setup Instructions
1. ​**​Download the datasets​**​ from either source
2. ​**​Place the datasets​**​ in the following directories:
    - `./data/DBP-FB/`for the DBP-FB dataset
    - `./data/WIKI-YAGO/`for the WIKI-YAGO dataset

### Running the Experiment
Execute the following command to start training and evaluation:
```
bash run.sh
```

### Configuration
Modify the `data_dir` parameter in `run.sh` to switch between datasets.

### Implementation References
Our implementation references the following approaches:
- ​**​AnyBURL​**​ implementation from [PyClause](https://github.com/symbolic-kg/PyClause)
- ​**​PARIS+​**​ implementation from [entity-matchers](https://github.com/epfl-dlab/entity-matchers)
