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
import os

from Bio import SeqIO

#%% Load GISAID fasta file

# fasta_all = 'data\\sequences\\gisaid_hcov-19_wisconsin-all_2021_03_24_21.fasta'
# fasta_b117 = 'data\\sequences\\gisaid_hcov-19_wisconsin-b117_2021_03_24_21.fasta'

fasta_all = 'data\\sequences\\gisaid_hcov-19_wisconsin-all_2021_04_10_20.fasta'
fasta_b117 = 'data\\sequences\\gisaid_hcov-19_wisconsin-b117_2021_04_10_20.fasta'


# fasta_all = 'data\\sequences\\gisaid_hcov-19_michigan-all_2021_03_24_22.fasta'
# fasta_b117 = 'data\\sequences\\gisaid_hcov-19_michigan-b117_2021_03_24_22.fasta'

def parse_fasta(fasta_file):    
    fasta_sequences = SeqIO.parse(open(fasta_file),'fasta')  
    cols = [[], [], []]
    
    # get only the metadata, discard the sequences
    for seq_record in fasta_sequences:
        record_id = seq_record.id
        components = record_id.split('|')
        cols[0].append(components[0])
        cols[1].append(components[1])
        cols[2].append(components[2])
        
    fasta_data = pd.DataFrame({'Virus name': cols[0],
                               'Accession ID': cols[1],
                               'Collection date': pd.to_datetime(cols[2])})
    
    return fasta_data

    
gisaid_all = parse_fasta(fasta_all)
gisaid_variants = parse_fasta(fasta_b117)

gisaid_all.to_csv('data\\sequences\\gisaid-all-WI.csv', index=False)
gisaid_variants.to_csv('data\\sequences\\gisaid-b117-WI.csv', index=False)

#%% Manual file

# gisaid_variants_file = 'data\\sequences\\gisaid_b117_manual_2021-03-11.csv'
# gisaid_variants = pd.read_csv(gisaid_variants_file)
# gisaid_variants['Collection date'] = pd.to_datetime(gisaid_variants['Collection date'])


#%% TSV files

path = 'data\\sequences'
tsv_all = 'gisaid_wisconsin_all_metadata_2021-04-10.tsv'

tsv_all = os.path.join(path, tsv_all)

temp = pd.read_csv(tsv_all, sep='\t')

 

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

var_count = count_by_week(gisaid_variants)
var_count.plot(x='Week of', y='Sequence count', kind='bar')   
    


#%% Percentage

var_count = var_count.set_index('Week of')
var_count['Total'] = seq_count.set_index('Week of')
var_count['Variants'] = var_count['Sequence count']
var_count['Variant fraction'] = var_count['Variants'] / var_count['Total']
# var_count['95% CI'] =  #hard!
var_count = var_count.reset_index()

var_count = var_count[var_count['Week of'] > datetime.datetime(2021, 1, 1)]
var_count = var_count[var_count['Week of'] <= datetime.datetime(2021, 3, 15)]

fig = px.line(var_count,
              x='Week of',
              y='Variant fraction',
              # color_discrete_sequence='orange',
              )

fig.update_layout(yaxis=dict(tickformat=".2%", range=[0, 0.2]), xaxis_range=[datetime.datetime(2021,1,17), datetime.datetime(2021, 4, 5)])
fig.update_traces(mode='lines+markers', line_color='orange', marker_color='orange', marker_symbol='cross')

# save as html, with plotly JS library loaded from CDN
htmlfile='docs\\assets\\plotly\\Variant-Fraction-GISAID.html'
fig.write_html(
    file=htmlfile,
    default_height=500,
    include_plotlyjs='cdn',
    )      

pngfile = 'docs\\assets\\Variant-Fraction-GISAID.png'
fig.write_image(
    pngfile,
    width=700,
    height=500,
    engine='kaleido',
    )

os.startfile(htmlfile)
os.startfile(pngfile)
