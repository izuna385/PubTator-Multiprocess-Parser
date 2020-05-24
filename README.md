# Multiprocessing PubTatorParser
## Quick Starts with NCBI-dataset
```
git clone https://github.com/izuna385/Multiprocessing_PubTatorParser.git
cd Multiprocessing_PubTatorParser
sh quick_start.sh
```

## Description
* Preprocessing PubTator-format documents to each mentions.

# Requirements
* Spacy (, or, [Scispacy](https://github.com/allenai/scispacy))

* multiprocess

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

  For more details, see `main.py`

* Each document takes about 100sec for preprocessing, under `en_core_sci_md` model.

* Under 24 core cpus and `en_core_sci_md` model, ~10GB RAM is needed.
  
# LISENCE

MIT
