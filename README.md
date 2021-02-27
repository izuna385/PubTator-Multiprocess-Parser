# Multiprocessing PubTator Parsing for Entity Linking
## Quick Starts with MedMentions, BC5CDR and NCBI-dataset
```
$ git clone https://github.com/izuna385/PubTator-Multiprocess-Parser.git
$ cd PubTator-Multiprocess-Parser
$ docker build -t multiprocess_pubtator .
$ docker run -itd multiprocess_pubtator /bin/bash

# In container
$ sh ./scripts/quick_start_Med_full.sh # for MedMentions
```
* You can run `quick_start_NCBI_full.sh`, too. If so, before running, make `pickled_doc_dir` empty.

* Note: If you use Mac, do `brew install wget` before running above script.

## Description
* Preprocessing PubTator-format documents to each mentions.

* If you are japanese, this might be useful for you.
  
  https://qiita.com/izuna385/items/d673694d25b2cf4efb89

# How to run
* Note: The following steps are entirely automated. 

  After building container, run `sh ./scripts/quick_start_[dataset_name]_full.sh`

## 1. Place PubTator format files to the `./dataset/`

* `corpus_pubtator.txt`, `corpus_pubtator_pmids_trng.txt`, `corpus_pubtator_pmids_dev.txt`, 
  and `corpus_pubtator_pmids_test.txt` must be placed there.
  
## 2. run

`python3 main.py`

## 3. Check

* Each Pubtator documents is preprocessed and dumped to  `./dataset/**pmid**.pkl`

  The format is as the below.
  
  ```
  {'title':title,  
   'abst':abst,
   'title_plus_abst': title_plus_abst,
   'pubmed_id': pubmed_id,
   'entities': entities,
   'split_sentence': splitted_sentence,
   'if_txt_length_is_changed_flag':if_txt_lenght_is_changed_flag,
   'lines':lines,
   'lines_lemma':lines_lemma
  }
  ```
  
  * The Key component is 'lines', in which all information for entity linking is included.

* Each document takes about 100sec for preprocessing, under `en_core_sci_md` model.

* Under 24 core cpus and `en_core_sci_md` model, ~10GB RAM is needed.

# LISENCE

MIT
