# WARNING: This script is only for checking parsing. For full parsing, run full.sh
mkdir dataset
cd dataset
git clone https://github.com/chanzuckerberg/MedMentions
cd ./MedMentions/full/data/
gzip -d corpus_pubtator.txt.gz
cp * ./../../../
cd ./../../../../
mkdir pickled_doc_dir
python3 main.py -debug True