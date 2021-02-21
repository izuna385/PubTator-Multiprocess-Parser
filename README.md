# Multiprocessing PubTator Parsing for Entity Linking
## Quick Starts with MedMentions-dataset and NCBI-dataset
```
$ git clone https://github.com/izuna385/Multiprocessing_PubTatorParser.git
$ cd Multiprocessing_PubTatorParser
$ docker build -t multiprocess_pubtator .
$ docker run -it multiprocess_pubtator /bin/bash

# In container
$ sh quick_start_Med_full.sh
```
* You can run `quick_start_NCBI_full.sh`, too.

* Note: If you use Mac, do `brew install wget` before running above script.

## Description
* Preprocessing PubTator-format documents to each mentions.

* If you are japanese, this might be useful for you.
  
  https://qiita.com/izuna385/items/d673694d25b2cf4efb89

# How to run

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
