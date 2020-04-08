import os
import numpy
import scipy
import spacy
import collections
import argparse
import re
import pickle

from collections import defaultdict
from spacy.symbols import ORTH, LEMMA

parser = argparse.ArgumentParser()
parser.add_argument('--window_size', type = int, required = False, default = 5, help = 'Determines the window size considered for calculating the scores.')
args = parser.parse_args()

spacy_model = spacy.load("en_core_web_sm")

novels = [os.path.join(root, novel_file) for root, direct, all_files in os.walk('novel_aficionados_dataset') for novel_file in all_files if 'ready_for_replication' in novel_file and 'wikipedia' not in root]

novel_collector = defaultdict(list)
novel2index = defaultdict(int)

for novel_index, novel in enumerate(novels):
    print(novel)
    results = defaultdict(list)
    novel2index[novel] = novel_index
    with open(novel) as r:
        tests = defaultdict(list)
        text = [l.strip('\n') for l in r.readlines()]
        co_oc = defaultdict(lambda : defaultdict(int))
        word2index = defaultdict(int)
        word_counter = defaultdict(int)

        print('Now collecting co-occurrences...')
        lemmatized_novel = []
        for line in text:
            if '#' in line or '$' in line:
                line_split = line.split()
                current_line_model = spacy_model(line)
                for w in line_split:
                    if '#' in w or '$' in w:
                        test_case = [{ORTH : w, LEMMA : w}]
                        spacy_model.tokenizer.add_special_case(w, test_case)
                spacy_line = [w.lemma_ for w in spacy_model(line)]
                lemmatized_novel.append(' '.join(spacy_line))
                for index, w in enumerate(spacy_line):
                    word_counter[w] += 1 
                    if '#' in w or '$' in w:
                        if w not in word2index.keys():
                            word2index[w] = len(word2index.keys())
                        relevant_slice = [spacy_line[i] for i in range(max(0, index - args.window_size), min(index + args.window_size, len(spacy_line)))]
                        #relevant_slice = [spacy_line[i] for i in range(max(0, index - args.window_size), min(index + args.window_size, len(spacy_line)))]
                        for relevant_word in relevant_slice:
                            if relevant_word not in word2index.keys():
                                word2index[relevant_word] = len(word2index.keys())
                            co_oc[word2index[w]][word2index[relevant_word]] += 1

        print('Now PPMIing...')
        index2word = {v : k for k, v in word2index.items()}
        novel_length = len([w for line in lemmatized_novel for w in line.split()])
        PMIS = defaultdict(lambda : defaultdict(int))
        for first_key, first_voc in co_oc.items():
            for second_key, value in first_voc.items():
                PMIS[first_key][second_key] = (max(0, numpy.log2((value/novel_length)/((word_counter[index2word[first_key]]/novel_length)*(word_counter[index2word[second_key]]/novel_length)))))

        print('Now calculating the informativeness of the windows...')
        for line in lemmatized_novel:
            if '#' in line or '$' in line:
                line_split = line.split()
                for index, w in enumerate(line_split):
                    if '#' in w or '$' in w:
                        counter = 0.0
                        relevant_slice = [line_split[i] for i in range(max(0, index - args.window_size), min(index + args.window_size, len(line_split)))]
                        #relevant_slice = [spacy_line[i] for i in range(max(0, index - args.window_size), min(index + args.window_size, len(spacy_line)))]
                        for relevant_word in relevant_slice:
                            counter =+ PMIS[word2index[w]][word2index[relevant_word]]
                            if '#' in w: 
                                results['common_nouns'].append(counter)
                            elif '$' in w: 
                                results['proper_names'].append(counter)

    for test, test_results in results.items():
        novel_collector[test].append(test_results)                

print('Now dumping...')
with open('pickles/PMI_window_{}.pickle'.format(args.window_size), 'wb') as o:
    pickle.dump([novel_collector, novel2index], o)
