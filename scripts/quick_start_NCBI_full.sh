
cd dataset
wget https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItrainset_corpus.zip
unzip NCBItrainset_corpus.zip
rm NCBItrainset_corpus.zip
wget https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBIdevelopset_corpus.zip
unzip NCBIdevelopset_corpus.zip
rm NCBIdevelopset_corpus.zip
wget https://www.ncbi.nlm.nih.gov/CBBresearch/Dogan/DISEASE/NCBItestset_corpus.zip
unzip NCBItestset_corpus.zip
rm NCBItestset_corpus.zip
cd ./../
mkdir pickled_doc_dir
python3 NCBIpreprocess.py
python3 main.py