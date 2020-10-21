#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 14:57:32 2020

@author: antonio
"""
import string
import unicodedata
import re
import argparse

def normalize_str(annot, min_upper, keep_accents=False, keep_punctuation=False):
    '''
    DESCRIPTION: normalize annotation: lowercase, remove extra whitespaces, 
    remove punctuation and remove accents.
    
    Parameters
    ----------
    annot: string
    min_upper: int. 
        It specifies the minimum number of characters of a word to lowercase 
        it (to prevent mistakes with acronyms).
    
    Returns
    -------
    annot_processed: string
    '''
    # Lowercase
    annot_lower = ' '.join(list(map(lambda x: x.lower() if len(x)>min_upper else x, annot.split(' '))))
    
    # Remove whitespaces
    annot_bs = re.sub('\s+', ' ', annot_lower).strip()

    # Remove punctuation
    if keep_punctuation == False:
        annot_punct = annot_bs.translate(str.maketrans('', '', string.punctuation))
    else:
        annot_punct = annot_bs
    
    # Remove accents
    if keep_accents==False:
        annot_final = remove_accents(annot_punct)
    else: 
        annot_final = annot_punct
    
    return annot_final

def remove_accents(data):
    return ''.join(x for x in unicodedata.normalize('NFKD', data) if x in string.printable)

def one_df_per_label(df, meddocan_labels):
    df_demo = df.loc[df['label'].isin(meddocan_labels) == True,:].copy()
    df_procedure = df.loc[df['label'] == 'PROCEDIMIENTO',:].copy()
    df_eo = df.loc[df['label'] == 'ENTIDAD-OBSERVABLE', :].copy()
    df_symptom = df.loc[df['label'] == 'SINTOMA',:].copy()
    df_disease = df.loc[df['label'] == 'ENFERMEDAD',:].copy()
    df_protein = df.loc[df['label'] == 'PROTEINAS',:].copy()
    df_medication = df.loc[df['label'] == 'FARMACO',:].copy()
    df_species  = df.loc[df['label'] == 'SPECIES',:].copy()
    
    
    return df_demo, df_procedure, df_eo, df_symptom, df_disease, df_protein, \
        df_medication, df_species
        
def argparser():
    '''
    DESCRIPTION: Parse command line arguments
    '''
    
    parser = argparse.ArgumentParser(description='process user given parameters')
    parser.add_argument("-d", "--datapath", required = True, dest = "path", 
                        help = "Path where I have the output of NER taggers "+ 
                        "with the directory structure of run-all-neuroner-models.sh")
    parser.add_argument("-n", "--ndocs", required = True, dest = "ndocs", 
                        help = "Number of docs on which NER taggers were run")   
    args = parser.parse_args()
    
    return args.path, int(args.ndocs)