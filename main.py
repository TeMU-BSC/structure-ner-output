#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:23:40 2020

@author: antonio
"""

from utils import one_df_per_label, argparser
from parse_ann import parse_ann
import os
from clean_ner_output import clean_ner_output
from obtain_statistics import obtain_statistics
from format_negation_uncertainty import integrate_negation_uncertainty
import time

if __name__ == '__main__':


    path, ndocs = argparser()
    
    # Create tmp and out directory
    if not os.path.exists(os.path.join(path, 'tmp')):
        os.mkdir(os.path.join(path, 'tmp')) 
    if not os.path.exists(os.path.join(path, 'out')):
        os.mkdir(os.path.join(path, 'out'))  
        
    #### 1. Parse NER outputs ####
    # OUTPUT: Dataframe with raw NER output: detected entites with the information
     # about their position and label
    print('Parsing NER outputs...')
    df = parse_ann(path)
    df = df.drop(['annotator', 'bunch', 'mark'], axis=1)
    df['filename'] = df['filename'].apply(lambda x: '.'.join(x.split('.')[:-1]))
    df['offset1'] = df['offset1'].astype(int)
    df['offset2'] = df['offset2'].astype(int)
    
    # NORMALIZABLES --> FARMACO, Remove UNCLEAR
    df['label'].replace('NORMALIZABLES', 'FARMACO', inplace=True)
    df = df.drop(df.loc[(df['label'] == "UNCLEAR")].index)
           
        
    #### 2. Add negation and uncertainty as column ###
    # TODO: modify all functions. Now dataframes have one extra column
    print('Formatting negation and uncertainty info...')
    t1 = time.time()
    df_neg = integrate_negation_uncertainty(df)
    print("Elapsed time since 'Formatting negation and uncertainty info...' message: "
          + str(round(time.time()-t1, 2)) + 's')
    
    # Get one dataframe per label
    # OUTPUT: One dataframe with raw NER output per entity
    meddocan_labels = ['FECHAS', 'HOSPITAL', 'TERRITORIO', 'EDAD-SUJETO-ASISTENCIA',
                       'CALLE', 'PAIS', 'NOMBRE-SUJETO-ASISTENCIA', 'PROFESION',
                       'SEXO-SUJETO-ASISTENCIA', 'NOMBRE-PERSONAL-SANITARIO',
                       'ID-SUJETO-ASISTENCIA', 'CORREO-ELECTRONICO']
    df_demo, df_proc, df_eo, df_symp, df_dis, df_prot, df_med, df_spec = \
        one_df_per_label(df_neg, meddocan_labels)
        
    #### 3. Clean NER outputs ####
    t1 = time.time()
    print('Cleaning NER outputs...')
    # 3.1. Normalize span (lowercase, remove extra whitespaces, remove punctuation)
    # 3.3. Remove empty spans or null
    # 3. OPT: Remove only numbers
    # 3.4. Reset index
    # 3. OPT: If one span_normalized have several labels, keep the most frequent label
    # 3.5. Remove duplicated entries & reset index
    # OUTPUT: One dataframe with clean NER output per entity. Clean means the text
     # span is normalized, there are not empty spans, there are not duplicated entities
     # (same filename, text position and label) and if one text span has several labels, 
     # I keep the most frequent label.
    df_demo_clean = clean_ner_output(df_demo, remove_only_numbers=False)
    df_eo_clean = clean_ner_output(df_eo)
    df_proc_clean = clean_ner_output(df_proc)
    df_symp_clean = clean_ner_output(df_symp)
    df_dis_clean = clean_ner_output(df_dis)
    df_prot_clean = clean_ner_output(df_prot)
    df_med_clean = clean_ner_output(df_med)
    df_spec_clean = clean_ner_output(df_spec)
    #del df_demo, df_eo, df_proc, df_symp, df_dis, df_prot, df_med, df_spec
    print("Elapsed time since 'Cleaning NER outputs...' message: "
          + str(round(time.time()-t1, 2)) + 's')
    
    #### 4. Obtain statistics ####
    t1 = time.time()
    print('Obtaining statistics...')
    # 4.1 Obtain list of documents where each entity is present
    # 4.2 Count term & document occurrences
    # 4.3 Add lemma
    # 4.4 Extract list of normalized terms
    # 4.5 Calculate Snomed IDs
    # 4.6 Drop useless columns
    # OUTPUT: One dataframe with statistics about NER outputs per entity. Statistics:
     # term and doc frequency, list of documents where it appears, lemma, SnomedID
    df_demo_final = obtain_statistics(df_demo_clean, path, 'demographics', ndocs)
    df_eo_final = obtain_statistics(df_eo_clean, path, 'observed_entity', ndocs)
    df_proc_final = obtain_statistics(df_proc_clean, path, 'procedure', ndocs)
    df_symp_final = obtain_statistics(df_symp_clean, path, 'symptom', ndocs)
    df_dis_final = obtain_statistics(df_dis_clean, path, 'disease', ndocs)
    df_prot_final = obtain_statistics(df_prot_clean, path, 'protein', ndocs)
    df_med_final = obtain_statistics(df_med_clean, path, 'medication', ndocs)
    df_spec_final = obtain_statistics(df_spec_clean, path, 'species', ndocs)
    #del df_demo_clean,df_eo_clean, df_proc_clean, df_symp_clean, df_dis_clean, df_prot_clean, df_med_clean, df_spec_clean
    print("Elapsed time since 'Obtaining statistics...' message: " 
          + str(round(time.time()-t1, 2)) + 's')

    
    #### 5. Export output ####
    df_demo_final.drop_duplicates(['span_normalized','filename']).\
        sort_values(by=['term_freq', 'span_lower'], ascending=False).\
        to_csv(os.path.join(path, 'out/terms_demographics.tsv'), sep='\t', 
               header=True, index=False)
    df_eo_final.drop_duplicates(['span_normalized','filename']).\
        sort_values(by=['term_freq', 'span_lower'], ascending=False).\
        to_csv(os.path.join(path, 'out/terms_observable_entity.tsv'), sep='\t', 
               header=True, index=False)
    df_proc_final.drop_duplicates(['span_normalized','filename']).\
        sort_values(by=['term_freq', 'span_lower'], ascending=False).\
        to_csv(os.path.join(path, 'out/terms_procedure.tsv'), sep='\t', 
               header=True, index=False)
    df_symp_final.drop_duplicates(['span_normalized','filename']).\
        sort_values(by=['term_freq', 'span_lower'], ascending=False).\
        to_csv(os.path.join(path, 'out/terms_symptom.tsv'), sep='\t', 
               header=True, index=False)
    df_dis_final.drop_duplicates(['span_normalized','filename']).\
        sort_values(by=['term_freq', 'span_lower'], ascending=False).\
        to_csv(os.path.join(path, 'out/terms_disease.tsv'), sep='\t', 
               header=True, index=False)
    df_prot_final.drop_duplicates(['span_normalized','filename']).\
        sort_values(by=['term_freq', 'span_lower'], ascending=False).\
        to_csv(os.path.join(path, 'out/terms_protein.tsv'), sep='\t', 
               header=True, index=False)
    df_med_final.drop_duplicates(['span_normalized','filename']).\
        sort_values(by=['term_freq', 'span_lower'], ascending=False).\
        to_csv(os.path.join(path, 'out/terms_medication.tsv'), sep='\t', 
               header=True, index=False)
    df_spec_final.drop_duplicates(['span_normalized','filename']).\
        sort_values(by=['term_freq', 'span_lower'], ascending=False).\
        to_csv(os.path.join(path, 'out/terms_species.tsv'), sep='\t', 
               header=True, index=False)
