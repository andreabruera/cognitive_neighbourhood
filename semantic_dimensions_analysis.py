import os
import numpy
import scipy
import spacy
import collections
import argparse
import re
import pickle

from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('--window_size', type = int, required = False, default = 10, help = 'Determines the window size considered for calculating the scores.')
parser.add_argument('--test', type = str, required = True, help = 'The test to be performed')
args = parser.parse_args()

if args.test == 'concreteness':
    concreteness_file = [(l.strip('\n')).split('\t') for l in open('tests/concreteness_norms_2014_for_proper_names_testing.txt').readlines()][1:]
    words_and_scores = {col[0] : float(col[1]) for col in concreteness_file}

elif args.test == 'imageability':
    imageability_file = [(l.strip('\n')).split('\t') for l in open('tests/glasgow_norms_for_proper_names_testing.txt').readlines()][1:]
    words_and_scores = {col[0] : float(col[3]) for col in imageability_file}
    imageability_file_multisyllabic = [(l.strip('\n')).split('\t') for l in open('tests/imageability_and_BOI_norms_for_proper_names_testing.txt').readlines()][1:]
    for l in imageability_file_multisyllabic:
        if l[0] not in words_and_scores.keys():
            words_and_scores[l[0]] = float(l[1])

elif args.test == 'valence':
    valence_file = [(l.strip('\n')).split('\t') for l in open('tests/valence_norms_2013_for_proper_names_testing.txt').readlines()][1:]
    words_and_scores = {col[0] : float(col[1]) for col in valence_file}

elif args.test == 'body_object_interaction':
    body_object_interaction_file_monosyllabic = [(l.strip('\n')).split('\t') for l in open('tests/body_object_ratings.txt').readlines()][1:]
    words_and_scores = {col[0] : float(col[1]) for col in body_object_interaction_file_monosyllabic}
    body_object_interaction_file_multisyllabic = [(l.strip('\n')).split('\t') for l in open('tests/imageability_and_BOI_norms_for_proper_names_testing.txt').readlines()][1:]
    for l in body_object_interaction_file_multisyllabic:
        words_and_scores[l[0]] = float(l[2])
    body_object_interaction_file_verb = [(l.strip('\n')).split('\t') for l in open('tests/verb_embodiment_norms_for_proper_names_testing.txt').readlines()][1:]
    for l in body_object_interaction_file_verb:
        words_and_scores[l[0]] = float(l[1])

spacy_model = spacy.load("en_core_web_sm")

novels = [os.path.join(root, novel_file) for root, direct, all_files in os.walk('novel_aficionados_dataset') for novel_file in all_files if 'ready_for' in novel_file and 'wikipedia' not in root]

novel_collector = defaultdict(list)
novel2index = defaultdict(int)
stats = []

print('Length of the full {} test: {}'.format(args.test, len(words_and_scores)))

for novel_index, novel in enumerate(novels):
    novel2index[novel] = novel_index
    with open(novel) as r:
        tests = defaultdict(list)
        text = [l for l in r.readlines()]
        lines_clean = [re.sub('\n|#|\$', '', l) for l in text]
        tests['common_nouns'] = [re.sub('\$|\n', '', re.sub(' #\w+# ', ' # ', l)) for l in text]
        tests['proper_names'] = [re.sub('#|\n', '', re.sub('\s\$\w+\$\s', ' $ ', l)) for l in text]
        
    word2index = defaultdict(int)
    index2score = defaultdict(float)
    for line in lines_clean:
        spacy_line = spacy_model(line)
        for w in spacy_line:
            if w.lemma_ not in word2index.keys() and w.lemma_ in words_and_scores.keys():
                word2index[w.lemma_] = len(word2index.keys())
                index2score[word2index[w.lemma_]] = words_and_scores[w.lemma_]
    stat_values = [v for k, v in index2score.items()]
    stats.append(stat_values)
    print('\n{}\n'.format(novel))
    print('Number of words considered for the current evaluation: {}'.format(len(stat_values)))
    print('Median concreteness value for the words to be considered: {}, std. {}'.format(numpy.median(stat_values), numpy.std(stat_values)))
    
    results = defaultdict(list)

    for test, test_lines in tests.items():
        for line in test_lines:
            if '#' in line or '$' in line:
                spacy_line = [w.lemma_ for w in spacy_model(line)]
                for index, w in enumerate(spacy_line):
                    if w == '#' or w == '$':
                        counter = 0.0
                        relevant_slice = [word2index[spacy_line[i]] for i in range(max(0, index - args.window_size), min(index + args.window_size, len(spacy_line)))]
                        #relevant_slice = [spacy_line[i] for i in range(max(0, index - args.window_size), min(index + args.window_size, len(spacy_line)))]
                        for relevant_word_index in relevant_slice:
                            counter += index2score[relevant_word_index]
                        results[test].append(counter) 
    for test, test_results in results.items():
        novel_collector[test].append(test_results)                
        print('{}: {}'.format(test, numpy.median(test_results)))

with open('{}_window_{}.pickle'.format(args.test, args.window_size), 'wb') as o:
    pickle.dump([novel_collector, stats], o)
