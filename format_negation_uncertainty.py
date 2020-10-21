#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 21 14:47:22 2020

@author: antonio
"""

def add_tag(df, other, label):
    tag_scope = df.loc[df['label'] == label, :].copy()
    tag_scope['offset'] = tag_scope[['offset1', 'offset2']].apply(tuple, axis=1)
    tag_dict = tag_scope.groupby(['filename'])['offset'].agg(list).to_dict()

    for k,v in tag_dict.items():
        other_this = other.loc[other['filename']==k,:]
        for pos in v:
            other.loc[other_this.loc[other_this.apply(lambda x: (pos[0]<=x['offset1']) & (x['offset2']<=pos[1]), axis=1),:].index,label] = 'Y'
    return other
            
def integrate_negation_uncertainty(df):
    other = df.loc[df['label'].isin(['NEG', 'UNC', 'NSCO','USCO']) == False, :].copy()
    other['NSCO'] = 'F'
    other['USCO'] = 'F'

    other_neg = add_tag(df, other, 'NSCO')
    other_unc = add_tag(df, other_neg, 'USCO')

        
    return other_unc
    