#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 15 12:48:32 2020

@author: antonio
"""

import pandas as pd
import numpy as np
from utils import normalize_str

def clean_ner_output(df, remove_only_numbers=True):
    '''
    Parameters
    --------
    df: DataFrame
        Columns: ['filename', 'label', 'offset1', 'offset2', 'span','NSCO', 'USCO']
    
    Returns
    -------
    df_dedup: DataFrame
        Pandas Dataframe with no empty spans, and no duplicated entries. Columns: 
            ['filename', 'label', 'offset1', 'offset2', 'span', 'span_normalized',
       'span_lower','NSCO', 'USCO']
    
    '''
    
    # 2.1. Normalize span (lowercase, remove extra whitespaces, remove punctuation)
    df['span_normalized'] = df['span'].\
        apply(lambda x: normalize_str(x, 3, keep_accents=False)) # Need this because doctors do not put accents properly
    df['span_lower'] = df['span'].\
        apply(lambda x: normalize_str(x, 3, keep_accents=True, keep_punctuation=True)) # Need this to use Carlos normalization tool and to show the results
    
    '''
    # 2. OPT: Remove MEDDOCAN predictions
    meddocan_labels = ['FECHAS', 'HOSPITAL', 'TERRITORIO', 'EDAD-SUJETO-ASISTENCIA',
                       'CALLE', 'PAIS', 'NOMBRE-SUJETO-ASISTENCIA', 'PROFESION', 
                       'SEXO-SUJETO-ASISTENCIA', 'NOMBRE-PERSONAL-SANITARIO', 
                       'ID-SUJETO-ASISTENCIA', 'CORREO-ELECTRONICO']
    df_not_demo = df.loc[df['label'].isin(meddocan_labels) == False,:].copy()
    df_demo = df.loc[df['label'].isin(meddocan_labels) == True,:].copy()
    
    # 2. OPT: NORMALIZABLES --> FARMACO
    df_not_demo['label'].replace('NORMALIZABLES', 'FARMACO', inplace=True)
    
    # 2. OPT: Remove UNCLEAR
    df_not_demo = df_not_demo.drop(df_not_demo.loc[(df_not_demo['label'] == "UNCLEAR")].index)
    '''
    # 2. OPT: Remove PROTEINAS and "covid19"
    df = df.drop(df.loc[((df['label'] == "PROTEINAS") &
                         (df['span_normalized'].isin(["covid19", "sarscov2", "cov2"])))].index)

    # 2.2. Remove empty spans or null
    df['span_normalized'].replace('', np.nan, inplace=True)
    df.dropna(inplace=True)
    
    # 2.3  OPT: Remove only numbers
    def str2Float(x):
        try:
            float(x)
            return np.nan
        except:
            return x
    if remove_only_numbers==True:
        span_norm_not_numbers = df['span_normalized'].apply(lambda x: str2Float(x))
        df = df.drop(['span_normalized'], axis=1)
        df = df.assign(span_normalized=span_norm_not_numbers.values)
        df.dropna(inplace=True)
    
    # 2.4. Reset index
    df.reset_index(drop=True, inplace=True)
    
    # 2.5 OPT: If one span_normalized have several labels, keep the most frequent label
    # Create dict to replace the duplicated span_normalized by the label which is most frequent
    if df.label.value_counts().shape[0]>1:
        aux = df.groupby(['span_normalized', 'label'], as_index=False)\
            .count()[['span_normalized', 'label', 'filename']].copy()
        aux.columns = ['span_normalized', 'label', 'count']
        aux = aux.sort_values(by=['count'])
        aux = aux.drop_duplicates(['span_normalized'], keep='last').copy()
        span_norm2label = dict(zip(aux.span_normalized, aux.label))
        # Replace
        for idx, row in df.iterrows():
            span_norm = df.loc[idx, 'span_normalized']
            if span_norm in span_norm2label.keys():
                df.loc[idx, 'label'] = span_norm2label[span_norm]
    
    
    # 2.6. Remove duplicated entries & reset index
    df_dedup = df.\
        drop_duplicates(subset=['filename','label', 'span', 'offset1', 'offset2']).copy()
    df_dedup.reset_index(drop=True, inplace=True)
    df_dedup = df_dedup[['filename', 'label', 'offset1', 'offset2','span', 
                         'span_normalized','span_lower','NSCO', 'USCO']]
    
    return df_dedup
