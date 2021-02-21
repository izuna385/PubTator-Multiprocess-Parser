cd dataset
git clone https://github.com/JHnlp/BioCreative-V-CDR-Corpus
cd BioCreative-V-CDR-Corpus
unzip CDR_Data.zip
cp CDR_Data/CDR.Corpus.v010516/*.txt ./../
cd ./../../
mkdir pickled_doc_dir
python3 main.py