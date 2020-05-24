import glob

def all_pmid_gettor(all_pmid_filepath):
    pmids = []
    with open(all_pmid_filepath, 'r') as f:
        for line in f:
            if line.strip():
                pmids.append(line)
    return len(pmids)

def progress(globdir):
    filepath_list = glob.glob(globdir)
    return len(filepath_list)

def progressbar(globdir, all_pmid_filepath):
    print('progress', progress(globdir=globdir), ' / ', all_pmid_gettor(all_pmid_filepath=all_pmid_filepath))

def type_statics_intrainingdatasetreturner(trng_pmid_path, corpus_pubtator_path):
    def trng_pmid_returner(trng_pmid_path):
        train_pmids = []
        with open(trng_pmid_path, 'r') as f:
            for line in f:
                pmid = line.strip()
                if pmid != '':
                    train_pmids.append(pmid)
        return train_pmids
    trng_pmids = trng_pmid_returner(trng_pmid_path=trng_pmid_path)
    all_train_anno = 0
    type_statics = {}
    unknowntypes = []

    with open(corpus_pubtator_path,'r') as f:
        for line in f:
            if not ('|t|' in line or '|a|' in line or line.strip() == ''):
                try:
                    annos = line.strip().split('\t')
                    pmid = annos[0]
                    types = annos[4]
                    types_list = types.split(',')

                    if pmid in trng_pmids: # We can only see train set
                        for type in types_list:
                            if type in type_statics:
                                type_statics[type] += 1
                            else:
                                type_statics[type] = 1

                            # if 'UnknownType' in types_list:
                            #     print(types_list)
                except:
                    print('typeparse_error',line)

    return type_statics

if __name__ == '__main__':
    GLOBDIR = './pickled_doc_dir/*'
    all_pmid_filepath = './corpus_pubtator_pmids_all.txt'

    progressbar(globdir=GLOBDIR, all_pmid_filepath=all_pmid_filepath)
    progressbar(globdir='./pickled_doc_dir/*', all_pmid_filepath=all_pmid_filepath)