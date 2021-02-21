# WARNING: This script is only for checking parsing. For full parsing, run full.sh
cd dataset
git clone https://github.com/chanzuckerberg/MedMentions
cd ./MedMentions/full/data/
gzip -d corpus_pubtator.txt.gz
cp * ./../../../
cd ./../../../../
python3 main.py -debug True