with open('./dataset/corpus_pubtator.txt', 'w') as cp:
    dataset = ['train', 'develop', 'test']
    for dataflag in dataset:
        with open('./dataset/NCBI'+dataflag+'set_corpus.txt', 'r') as rawdata:
            pmids = []

            for idx, line in enumerate(rawdata):
                if idx == 0 and dataflag == 'train':
                    continue # skip \n
                cp.write(line)
                if '|t|' in line[:15]:
                    pmid = line.split('|')[0]
                    pmids.append(pmid)

            if dataflag == 'train':
                pmidtxtpath = './dataset/' + 'corpus_pubtator_pmids_trng.txt'
            elif dataflag == 'develop':
                pmidtxtpath = './dataset/' + 'corpus_pubtator_pmids_dev.txt'
            else:
                pmidtxtpath = './dataset/' + 'corpus_pubtator_pmids_test.txt'

            with open(pmidtxtpath, 'w') as pt:
                for idx, pmid in enumerate(pmids):
                    if idx == 0:
                        pt.write(pmid)
                    else:
                        pt.write('\n'+pmid)