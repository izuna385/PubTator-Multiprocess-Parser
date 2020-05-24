import spacy
import glob
import json
from multiprocessing import Pool
import multiprocessing as multi
from tqdm import tqdm
import pickle
import scispacy
from spacy.symbols import ORTH
import time
from utils import progressbar, type_statics_intrainingdatasetreturner
import re
import argparse
import sys
from config import Config

conf_class = Config()
opts = conf_class.get_params()
PICKLED_DOC_DIR = opts.pickled_doc_dir

def onepmid_contents_returner(one_pmid_filepath):
    contents_list = list()

    with open(one_pmid_filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line:
                contents_list.append(line)
    return contents_list


def trng_pmid_returner(trng_pmid_path):
    train_pmids = []
    with open(trng_pmid_path,'r') as f:
        for line in f:
            pmid = line.strip()
            if pmid != '':
                train_pmids.append(pmid)
    return train_pmids

def process_contets_list(lines, type_statistics_json): # lines: contents_list
    pubmed_id, _, title = [x.strip() for x in lines[0].split("|", maxsplit=2)]
    _, _, abstract = [x.strip() for x in lines[1].split("|", maxsplit=2)]
    entities = []
    for entity_line in lines[2:]:
        _, start, end, mention, mention_type, umls_id = entity_line.split("\t")
        types_list = mention_type.split(",")

        if 'UnknownType' in types_list:
            continue
        if len(types_list) == 1:

            entities.append([int(start), int(end),
                                         mention, types_list[0], umls_id])
        else:
            annotated_types_dict = {}

            for one_type in types_list:
                annotated_types_dict.update({one_type:type_statistics_json[one_type]})

            sorted_annotated_types = sorted(annotated_types_dict.items(), key = lambda  x : x[1], reverse= True)
            # sorted(type_statics.items(), key = lambda x : x[1], reverse=True)
            annotated_types = sorted_annotated_types[0][0]

            entities.append([int(start), int(end),
                                         mention, annotated_types, umls_id])

    return title, abstract, title + ' ' + abstract, pubmed_id, entities

def entities_and_splited_sentence_to_lines(split_sentence_from_nlp, entities):
    '''
    entities: [int(start), int(end),mention, types_list[0], umls_id]
    :param split_sentence_from_nlp:
    :param entities:
    :return:
    '''

    entities_for_each_sentence = list([] for _ in range(len(split_sentence_from_nlp)))

    offset_charlist = list()
    for i, sentence in enumerate(split_sentence_from_nlp):
        if i == 0:
            offset_charlist.append(0)
        else:
            char_offset = len(' '.join(split_sentence_from_nlp[0:i]))
            offset_charlist.append(char_offset)
    offset_charlist.append(len(' '.join(split_sentence_from_nlp))) # all texts

    for entity in entities:

        start = entity[0]
        end = entity[1]
        # mention = entities[2]
        # type = entities[3]
        # umls_id = entities[4]

        for j, char_offset in enumerate(offset_charlist):
            if char_offset <= int(start) and int(start) <= offset_charlist[j+1] and  char_offset <= int(end) and int(end) <= offset_charlist[j+1]:
                entities_for_each_sentence[j].append(entity)

    train_dev_test_lines, train_dev_test_lines_lemma = offset_charlist_and_sentence_split2lines(offset_charlist=offset_charlist,
                                                                    split_sentences=split_sentence_from_nlp,
                                                                    entities_for_each_sentence=entities_for_each_sentence)
    return train_dev_test_lines, train_dev_test_lines_lemma

def offset_charlist_and_sentence_split2lines(offset_charlist, split_sentences, entities_for_each_sentence):

    train_dev_test_lines = list()
    train_dev_test_lines_lemma = list()


    offset_char = offset_charlist[0:len(offset_charlist)]
    entities_for_each_sentence_offset_considered = list()

    for i, entities_in_one_sentence in enumerate(entities_for_each_sentence):
        offset_considered_entities = list()

        if entities_for_each_sentence == []:
            entities_for_each_sentence_offset_considered.append(offset_considered_entities)
            continue

        for entity in entities_in_one_sentence:

            start = entity[0] - offset_char[i]
            end = entity[1] - offset_char[i]
            mention = entity[2]
            type = entity[3]
            umls_id = entity[4]

            offset_considered_entities.append([start, end, mention, type, umls_id])

        entities_for_each_sentence_offset_considered.append(offset_considered_entities)

    '''
    print(train_lines[0]))
    C4308010	T116	DCTN4	<target> DCTN4 </target> as a modifier of chronic Pseudomonas aeruginosa infection in cystic fibrosis Pseudomonas aeruginosa (Pa) infection in cystic fibrosis ( CF ) patients is associated with worse long-term pulmonary disease and shorter survival , and chronic Pa infection ( CPA ) is associated with reduced lung function , faster rate of lung decline , increased rates of exacerbations and shorter survival .
    '''

    for idx, (one_split_sentence, entities_in_one_sent) in enumerate(zip(split_sentences, entities_for_each_sentence_offset_considered)):
        if entities_in_one_sent == []:
            continue
        # print('ENTITIES IN ONE SENT',entities_in_one_sent)
        for entity_in_one_sent in entities_in_one_sent:
            start = entity_in_one_sent[0]
            if start != 0:
                start = start -1
            end = entity_in_one_sent[1]
            mention = entity_in_one_sent[2]
            type = entity_in_one_sent[3]
            umls_id = entity_in_one_sent[4]

            sentence_text_list = list(one_split_sentence).copy()
            to_be_replaced_mention = ' <target> ' + mention + ' </target> '
            # print()
            # print('end char', sentence_text_list[start:end])
            # try:
            #     print('sentence end', sentence_text_list[end])
            # except:
            #     print('sentence end', sentence_text_list[start:end])

            if sentence_text_list[start] not in list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
                start += 1

            if end == len(sentence_text_list):
                if sentence_text_list[start:end][-1] not in list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
                    sentence_text_list[start:end-1] = list(to_be_replaced_mention)
                else:
                    sentence_text_list[start:end] = list(to_be_replaced_mention)
            elif sentence_text_list[start:end][-1] not in list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'):
                sentence_text_list[start:end-1] = list(to_be_replaced_mention)
            else:
                sentence_text_list[start:end] = list(to_be_replaced_mention)

            mention_replaced_sentence = ''.join(sentence_text_list)

            final_tokenized_sentence, final_tokenized_sentence_lemma = final_tokenization_after_targetflag_inverted(mention_replaced_sentence)

            train_dev_test_lines.append(umls_id + '\t' + type + '\t' + mention + '\t' + final_tokenized_sentence)
            train_dev_test_lines_lemma.append(umls_id + '\t' + type + '\t' + mention + '\t' + final_tokenized_sentence_lemma)

    return train_dev_test_lines, train_dev_test_lines_lemma

def final_tokenization_after_targetflag_inverted(mention_replaced_sentence):
    nlp_for_tokens = spacy.load('en_core_sci_md')
    nlp_for_tokens.tokenizer.add_special_case('<target>', [{ORTH: '<target>'}])
    nlp_for_tokens.tokenizer.add_special_case('</target>', [{ORTH: '</target>'}])
    tokens = []
    tokens_lemma = []
    for token in nlp_for_tokens(mention_replaced_sentence):
        tokens.append(token.text)
        if token.lemma_ != '-PRON-':
            tokens_lemma.append(token.lemma_)
        else:
            tokens_lemma.append(token.lower_)

    doublespace_trimed_sent = ' '.join(' '.join(tokens).split())
    doublespace_trimed_sent_lemma = ' '.join(' '.join(tokens_lemma).split())

    return doublespace_trimed_sent, doublespace_trimed_sent_lemma

def target_split_2_back(final_tokenization_sentence):
    token_list = list()
    ignore_idx = []
    # print(final_tokenization_sentence)
    for i, token in enumerate(final_tokenization_sentence):
        if i in ignore_idx:
            continue
        elif token == '<':

            try:
                # print(final_tokenization_sentence[i:i+3])
                if (final_tokenization_sentence[i+1] == 'target' ) and ('>' in final_tokenization_sentence[i+2]):
                    ignore_idx += [j for j in range(i, i+3)]

                    if final_tokenization_sentence[i+1] == 'target':
                        token_list.append('<target>')
                        continue
            except:
                pass

            try:
                # print(final_tokenization_sentence[i:i+3])
                if (final_tokenization_sentence[i+1] == '/' and (final_tokenization_sentence[i+1] == '/target')) and ('>' in final_tokenization_sentence[i+2]):
                    ignore_idx += [j for j in range(i, i+2)]

                    if final_tokenization_sentence[i+1] == '/target':
                        token_list.append('</target>')
                        continue
            except:
                pass
        else:
            token_list.append(token)
    # print(' '.join(token_list))
    return ' '.join(token_list)

def one_pmid_path2linesadded_allinfo_pkl(one_pmid_path):


    t1_ = time.time()
    title, abst, title_plus_abst, pubmed_id, entities, splitted_sentence, if_txt_lenght_is_changed_flag = one_pmid_path2allinfo(one_pmid_path=one_pmid_path)
    lines, lines_lemma = entities_and_splited_sentence_to_lines(split_sentence_from_nlp= splitted_sentence,
                                                   entities= entities)
    # for line in lines:
    #     print(line)
    new_pickled_path = PICKLED_DOC_DIR + str(pubmed_id) + '.pkl'
    with open(new_pickled_path, 'wb') as fff:
        pickle.dump({'title':title,
                     'abst':abst,
                     'title_plus_abst': title_plus_abst,
                     'pubmed_id': pubmed_id,
                     'entities': entities,
                     'split_sentence': splitted_sentence,
                     'if_txt_length_is_changed_flag':if_txt_lenght_is_changed_flag,
                     'lines':lines,
                     'lines_lemma':lines_lemma}
                    ,fff)
    t2_ = time.time()

    print('ONE DOC preprocess time', t2_-t1_,'sec')
    preprocessed_doc_length = glob.glob(PICKLED_DOC_DIR + '*')
    if len(preprocessed_doc_length) % 100 == 0:
        GLOBDIR = PICKLED_DOC_DIR + '*'
        all_pmid_filepath = './dataset/corpus_pubtator_pmids_all.txt'
        progressbar(globdir=GLOBDIR, all_pmid_filepath=all_pmid_filepath)
    # return title, abst, title_plus_abst, pubmed_id, entities, splitted_sentence, if_txt_lenght_is_changed_flag, lines

def one_pmid_path2allinfo(one_pmid_path):
    type_statistics_json = TYPE_STATISTICS_JSON
    spacy_model = spacy.load('en_core_sci_md')
    spacy_model.add_pipe(prevent_sentence_boundaries, before="parser")

    contents = onepmid_contents_returner(one_pmid_filepath=one_pmid_path)
    title, abst, title_plus_abst, pubmed_id, entities = process_contets_list(lines=contents,
                                                                             type_statistics_json=type_statistics_json)
    splitted_sentence, if_txt_lenght_is_changed_flag = title_and_abst2sentencelist(title=title,
                                                                                   abstract=abst,
                                                                                   nlp=spacy_model)
    if if_txt_lenght_is_changed_flag > 0:
        print('txt length is added during sentence split, be careful.',pubmed_id)
        print()

    # entities: [int(start), int(end),mention, types_list[0], umls_id]
    return title, abst, title_plus_abst, pubmed_id, entities, splitted_sentence, if_txt_lenght_is_changed_flag

def split_filepathlist2each_pmid_lines_and_allinfo_included_pkl(split_med_filepathlist):
    n_cores = multi.cpu_count()
    p = Pool(n_cores)
    p.map(one_pmid_path2linesadded_allinfo_pkl, split_med_filepathlist)

def one_pmid_path2mistakeflag(one_pmid_path):

    type_statistics_json = TYPE_STATISTICS_JSON
    spacy_model = spacy.load('en_core_sci_md')
    spacy_model.add_pipe(prevent_sentence_boundaries, before="parser")

    contents = onepmid_contents_returner(one_pmid_filepath=one_pmid_path)
    title, abst, title_plus_abst, pubmed_id, entities = process_contets_list(lines=contents,
                                                                             type_statistics_json=type_statistics_json)
    splitted_sentence, if_txt_lenght_is_changed_flag = title_and_abst2sentencelist(title=title,
                                                                                   abstract=abst,
                                                                                   nlp=spacy_model)
    if if_txt_lenght_is_changed_flag > 0:
        print(pubmed_id)
        print()

    # return title, abst, title_plus_abst, pubmed_id, entities, splitted_sentence, if_txt_lenght_is_changed_flag
    return if_txt_lenght_is_changed_flag

def title_and_abst2sentencelist(title, abstract, nlp):
    '''
    :param abst_txt:
    :return: splitted abst, is split OK?
    '''

    splitted_sentence_list = list()
    initial_txt_length = len(title + ' ' + abstract)


    title_parsed = nlp(title)
    abst_parsed = nlp(abstract)

    for span in title_parsed.sents:
        splitted_sentence_list.append(span.text)

    for span_ in abst_parsed.sents:
        splitted_sentence_list.append(span_.text)

    if_txt_lenght_is_changed_flag = splitted_sentence_and_txtlength_checker(splitted_sentence_list,initial_txt_length)

    # print(splitted_sentence_list)

    return splitted_sentence_list, if_txt_lenght_is_changed_flag

def splitted_sentence_and_txtlength_checker(splitted_sentence_list, initial_txt_length):
    after_split_txt_length = len(' '.join(splitted_sentence_list))
    if initial_txt_length != after_split_txt_length:
        print('LENGTH add', after_split_txt_length - initial_txt_length)
        return 1
    else:
        return 0

def splitted_meds_gettor(dirpath_for_glob):
    filelist = glob.glob(dirpath_for_glob)
    return filelist

def train_dev_test_pmid_returner(pmid_datadir):
    train = all_datadir + 'corpus_pubtator_pmids_trng.txt'
    dev = all_datadir + 'corpus_pubtator_pmids_dev.txt'
    test = all_datadir + 'corpus_pubtator_pmids_test.txt'

    return pmid_list_returner(train), pmid_list_returner(dev), pmid_list_returner(test)

def pmid_list_returner(txtpath):
    pmid_list = list()
    with open(txtpath, 'r') as f:
        for line in f:
            if line.strip() != '':
                pmid_list.append(line.strip())
    return pmid_list


def prevent_sentence_boundaries(doc):
    for i, token in enumerate(doc):
        if not can_be_sentence_start(token, doc):
            token.is_sent_start = False
    return doc

def can_be_sentence_start(token, doc):
    if token.i == 0:
        # print('TOKEN I',token, token.i)
        return True
    # We're not checking for is_title here to ignore arbitrary titlecased
    # tokens within sentences
    # elif token.is_title:
    #    return True

    elif str(token.nbor(-1).text + token.nbor(0).text ) in doc.text:
        try:
            if str(token.nbor(-1).text + token.nbor(0).text + token.nbor().text) in doc.text:
                # print(str(token.nbor(-1).text + token.nbor(0).text + token.nbor().text))
                return False
            else:
                pass
        except:
            pass

    elif token.nbor(-1).is_punct:
        return True
    elif token.nbor(-1).is_space:
        return True
    else:
        return False

def split_pubtator2pmid(input_file_path, output_data_dir, suffix='.one_p'):
    '''

    :param input_file_path:
    :return:  each pmid document
    '''
    dummy_list = []
    temp_list = []
    counter = 0
    with open(input_file_path, 'r') as f:
        for line in f:
            temp_list.append(line)
            if line.strip() == '':
                temp_pmid = int(re.split(r'\|', temp_list[0].rstrip(), maxsplit=2)[0])
                temp_path_for_one_pmid = output_data_dir + str(temp_pmid) + suffix

                with open(temp_path_for_one_pmid, 'w') as gg:
                    for one_line in temp_list:
                        gg.write(one_line)

                temp_list = dummy_list.copy()
                counter += 1

                if counter % 200 == 0:
                    print(counter, 'documents are splitted')

def one_pmid_path2entities(one_pmid_path ,type_statistics_json_path):
    with open(type_statistics_json_path, 'r') as g:
        type_statistics_json = json.load(g)

    contents = onepmid_contents_returner(one_pmid_filepath=one_pmid_path)
    title, abst, title_plus_abst, pubmed_id, entities = process_contets_list(lines=contents,
                                                                             type_statistics_json=type_statistics_json)
    return pubmed_id, entities


if __name__ =='__main__':
    EACH_DOC_DIRPATH = './pickled_doc_dir/'
    FORGLOB_DIRPATH = "./pickled_doc_dir/*"
    all_datadir = './dataset/'
    CORPUS_PUBTATOR = all_datadir + 'corpus_pubtator.txt'
    split_pubtator2pmid(input_file_path=CORPUS_PUBTATOR, output_data_dir=EACH_DOC_DIRPATH)

    # train/dev/test pmid is shared
    train_pmid, dev_pmid, test_pmid = train_dev_test_pmid_returner(pmid_datadir=all_datadir)
    TYPE_STATISTICS_JSON = type_statics_intrainingdatasetreturner(trng_pmid_path=all_datadir+'corpus_pubtator_pmids_trng.txt',
                                                                  corpus_pubtator_path=CORPUS_PUBTATOR)
    splitted_doc_filepathlist = splitted_meds_gettor(dirpath_for_glob=FORGLOB_DIRPATH)
    split_filepathlist2each_pmid_lines_and_allinfo_included_pkl(split_med_filepathlist=splitted_doc_filepathlist)
    print('dataset preprocessing end')

