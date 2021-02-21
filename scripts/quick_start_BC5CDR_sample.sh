# WARNING: This script is only for checking parsing. For full parsing, run full.sh
cd dataset
git clone https://github.com/JHnlp/BioCreative-V-CDR-Corpus
cd BioCreative-V-CDR-Corpus
unzip CDR_Data.zip
cp CDR_Data/CDR.Corpus.v010516/*.txt ./../
cd ./../../
python3 BC5CDRpreprocess.py
python3 main.py -debug True