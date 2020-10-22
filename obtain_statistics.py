#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct 19 12:04:36 2020

@author: antonio
"""
import pandas as pd
import os
from Med_Tagger import Med_Tagger
import subprocess
import numpy as np
import time

tag = Med_Tagger()


def obtain_statistics(df, path, label, ndocs):
    '''
    Obtain statistics from dataframe. Important: THIS CODE MUST NOT REMOVE ANY
    ROW FROM DF. PREPROCESSING STUFF SHOULD BE IN clean_ner_output.py
    
    Parameters
    --------
    df: DataFrame
        Pandas dataframe with columns: ['filename', 'label', 'offset1', 'offset2',
                                        'span', 'span_normalized','span_lower',
                                        'NSCO', 'USCO']
    path: string
        route to output parent directory
        
    Returns 
    -------
    df_final: DataFrame
        Pandas dataframe with columns: ['span_lower', 'label', 'doc_freq', 
                                        'doc_perc(%)', 'term_freq', 'lemma', 
                                        'snomedid', 'original_span', 
                                        'span_normalized', 'NSCO', 'USCO','filename']
    '''
    
    # 3.1 Obtain list of documents where each entity is present 
    # Obtain the same list with the entity not negated
    aux = df.groupby(['span_normalized', 'label'])['filename'].apply(list)
    aux_neg = df.loc[df['NSCO']=='F',:].groupby(['span_normalized', 'label'])['filename'].apply(list)
    aux_unc = df.loc[df['USCO']=='F',:].groupby(['span_normalized', 'label'])['filename'].apply(list)
    aux = aux.apply(lambda x: list(set(x))).rename('filename_list')
    aux_neg = aux_neg.apply(lambda x: list(set(x))).rename('filename_neg')
    aux_unc = aux_unc.apply(lambda x: list(set(x))).rename('filename_unc')
    df = df.merge(aux, how='left', on=['span_normalized', 'label'])
    df = df.merge(aux_neg, how='left', on=['span_normalized', 'label'])
    df = df.merge(aux_unc, how='left', on=['span_normalized', 'label'])
    df = df.drop(['filename'], axis=1).copy()
    df.columns = ['label', 'offset1', 'offset2', 'span', 'span_normalized',
                  'span_lower','NSCO', 'USCO','filename', 'filename_positive',
                  'filename_certain']
    df.loc[df['filename_positive'].isnull(),'filename_positive'] = \
    df.loc[df['filename_positive'].isnull(),'filename_positive'].apply(lambda x: [])
    df.loc[df['filename_certain'].isnull(),'filename_certain'] = \
    df.loc[df['filename_certain'].isnull(),'filename_certain'].apply(lambda x: [])
    
    # 3.2 Count term & document occurrences
    # TODO: Count separately and together the occurrences of the same term with 
    # different label (I have lost this information in clean_ner_output.py)
    df['doc_freq'] = df['filename'].apply(lambda x: len(x))
    df['filename'] = df['filename'].apply(lambda x: ', '.join(x))
    df['filename_positive'] = df['filename_positive'].apply(lambda x: ', '.join(x))
    df['filename_certain'] = df['filename_certain'].apply(lambda x: ', '.join(x))
    df['doc_perc(%)'] = df['doc_freq'].apply(lambda x: round(100*(x/ndocs), 2))
    term_freq = df['span_normalized'].value_counts()
    
    # Assign term freq
    df['term_freq'] = 0
    for idx, row in df.iterrows():
        span_norm = df.loc[idx, 'span_normalized']
        df.loc[idx, 'term_freq'] = term_freq[span_norm]
    
    # 3.3 Add lemma
    print('Adding lemma...')
    start = time.time()
    # TODO: Med_Tagger sometimes fails. Need to do some research here
    # TODO: Solve issue: PROBABILITIES: Empty ambiguity class for word 'díaz'. Duplicate NP analysis??
    df['lemma'] = ''
    for idx, row in df.iterrows():
        span_norm = df.loc[idx, 'span_lower']
        try:
            df.loc[idx, 'lemma'] = \
            ' '.join(list(map(lambda x: x[1], tag.parse(span_norm))))
        except:
            df.loc[idx, 'lemma'] = \
                ' '.join(list(map(lambda x: x[1], tag.parse(span_norm))))
    print("Elapsed time since 'Adding lemma...' message: "
          + str(round(time.time()-start, 2)) + 's')
    
    # 3.4 Extract list of normalized terms
    df['span_lower'].to_csv(os.path.join(path, 'tmp/terms_to_map_' + label + '.txt'), 
               header=None,index=False)
    
    # 3.5 Calculate Snomed IDs
    # TODO: There is a bug in TEMUnormalizer and some terms are not present in
    # TEMUnormalizer output. Need to do some research here
    # Merge normalized terms with existing DataFrame
    run_normalizer = input("Run TEMUnormalizer.py for label {}?".format(label) + " Type 'Y' for YES, any other key for NO: ")
    #run_normalizer = 'y'
    if run_normalizer.lower() == 'y':
        print('Calculating Snomed IDs with TEMUnormalizer...')
        start = time.time()
        cwd = os.getcwd()
        command1 = 'cd /home/antonio/resources/tools/TEMUNormalizer'
        command2 = ('python TEMUnormalizer.py -t ' + 
                    os.path.join(path, 'tmp/terms_to_map_' + label + '.txt') +
                    ' -f ' + os.path.join(path, 'tmp/mapped_list_snomed_' + label + '.tsv'))
        command3 = 'cd ' + cwd
        process = subprocess.Popen(command1 + ' && ' + command2 + ' && ' + command3,
                                   shell=True, stdout=subprocess.PIPE)
        process.wait()
        print("Elapsed time since 'Calculating Snomed IDs with TEMUnormalizer...' message: "
          + str(round(time.time()-start, 2)) + 's')
        
    df_snomed = pd.read_csv(os.path.join(path, 'tmp/mapped_list_snomed_' + label + '.tsv'),
                            sep='\t', header=None, 
                            names=['span_lower', 'snomedid', 'confidence'])
    df_final = df.merge(df_snomed, how='left', on='span_lower')
        
    
    # 3.6 Drop useless columns
    df_final = df_final.drop(['confidence'], axis=1)
    df_final = df_final[['span_lower', 'label', 'doc_freq', 'doc_perc(%)', 
                         'term_freq', 'lemma', 'snomedid', 'span',
                         'span_normalized','NSCO', 'USCO','offset1', 'offset2', 
                         'filename', 'filename_positive', 'filename_certain']].copy()
    df_final.columns = ['span_lower', 'label', 'doc_freq', 'doc_perc(%)', 
                         'term_freq', 'lemma', 'snomedid', 'original_span', 
                         'span_normalized','NSCO', 'USCO', 'offset1', 'offset2', 
                         'filename', 'filename_positive', 'filename_certain']
    
    return df_final
