# -*- coding: utf-8 -*-
"""
Created on Mon Mar  8 20:29:49 2021

@author: matt_
"""

import covid

import pandas as pd
import numpy as np
import plotly.express as px
import datetime

from Bio import SeqIO

#%% Load GISAID fasta file

input_file = 'data\\sequences\\gisaid_hcov-19_wisconsin_2021_03_11_17.fasta'

fasta_sequences = SeqIO.parse(open(input_file),'fasta')


cols = [[], [], []]

for seq_record in fasta_sequences:
    record_id = seq_record.id
    components = record_id.split('|')
    cols[0].append(components[0])
    cols[1].append(components[1])
    cols[2].append(components[2])
    
gisaid_all = pd.DataFrame({'Virus name': cols[0],
                           'Accession ID': cols[1],
                           'Collection date': pd.to_datetime(cols[2])})


#%% Plot sequences by collection dates
# gisaid_all['Week'] = gisaid_all['Collection date'].apply(lambda x: x.isocalendar()[1])

def count_by_week(gisaid_data):       
    gisaid_work = gisaid_data.copy()
    gisaid_work['Week of'] = gisaid_work['Collection date'].apply(lambda d: d - datetime.timedelta(days=d.weekday()))
    
    seq_count = gisaid_work.groupby('Week of').count()
    seq_count['Sequence count'] = seq_count['Virus name']
    seq_count = seq_count['Sequence count']
    seq_count = seq_count.reset_index(drop=False)
    
    return seq_count

seq_count = count_by_week(gisaid_all)

seq_count.plot(x='Week of', y='Sequence count', kind='bar')    
    
#%% Manual file

gisaid_variants_file = 'data\\sequences\\gisaid_b117_manual_2021-03-11.csv'
gisaid_variants = pd.read_csv(gisaid_variants_file)
gisaid_variants['Collection date'] = pd.to_datetime(gisaid_variants['Collection date'])

var_count = count_by_week(gisaid_variants)
var_count.plot(x='Week of', y='Sequence count', kind='bar')    

#%% Percentage

var_frac = var_count.set_index('Week of') / seq_count.set_index('Week of')


