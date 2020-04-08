import pickle
import os
import collections
import numpy
import scipy
import re

from scipy.stats.morestats import wilcoxon
from collections import defaultdict

tests = ['PMI', 'body_object_interaction', 'valence', 'concreteness', 'imageability']

for test in tests:
    for individual_pickle in os.listdir('pickles'):
        if test in individual_pickle:
            print('\n{}\n'.format(re.sub('.pickle', '', individual_pickle)))
            final_results = defaultdict(list)
            with open('pickles/{}'.format(individual_pickle), 'rb') as input:
                evaluations = pickle.load(input)[0]
                for test_type, test_results in evaluations.items():
                    for single_novel in test_results:
                        median_within_novel = numpy.median(single_novel)
                        #var_within_novel = numpy.var(single_novel)
                        final_results[test_type].append(median_within_novel)
                        #final_results[test_type].append(var_within_novel)

            print('Median for common nouns: {}'.format(numpy.median(final_results['common_nouns'])))
            print('Median for proper names: {}'.format(numpy.median(final_results['proper_names'])))
            z_value, p_value = wilcoxon(final_results['common_nouns'][:59], final_results['proper_names'][:59])
            print('\nP-value: {}\nEffect size: {}'.format(p_value, abs(z_value/numpy.sqrt(len(final_results['common_nouns'][:59])))))

            ### STD
            #print('Variance for common nouns: {}'.format(numpy.var(final_results['common_nouns'])))
            #print('Variance for proper names: {}'.format(numpy.var(final_results['proper_names'])))
            #z_value, p_value = wilcoxon(final_results['common_nouns'][:59], final_results['proper_names'][:59])
            #print('\nP-value: {}\nEffect size: {}'.format(p_value, abs(z_value/numpy.sqrt(len(final_results['common_nouns'][:59])))))
