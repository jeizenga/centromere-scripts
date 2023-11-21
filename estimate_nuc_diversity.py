#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 13:53:20 2023

@author: Jordan
"""

import sys
import os
import re

def parse_cigar(cigar):
    parsed = []
    for m in re.finditer("(\d+)([HSNMIDX=])", cigar):
        parsed.append((m.group(2), int(m.group(1))))
    return parsed

def count_aligned(cigar):
    aligned = 0
    for op, l in cigar:
        if op == "M" or op == "X" or op == "=":
            aligned += l
            
    return aligned

if __name__ == "__main__":
    
    if len(sys.argv) != 3:
        print("usage: estimate_nuc_diveristy.py snp_mat.tsv pairwise_aln_prefix")
        exit(1)
        

    prefix = os.path.abspath(sys.argv[2])
    cigar_dir = os.path.dirname(prefix)
    cigar_file_prefix = os.path.basename(prefix)

    cigar_files = [os.path.join(cigar_dir, f) for f in os.listdir(cigar_dir) if f.startswith(cigar_file_prefix)]


    total_aligned = 0
    for cigar_file in cigar_files:
        with open(cigar_file) as f:
            cigar = parse_cigar(f.read().strip())
            total_aligned += count_aligned(cigar)

    
    column_count = None
    
    with open(sys.argv[1]) as f:
        
        # discard the header
        next(f)
        
        # parse the data
        for line in f:
            tokens = line.strip().split()
            # skip the sample identifier
            if column_count is None:
                column_count = [[0, 0] for i in range(len(tokens) - 1)]
                
            for i in range(1, len(tokens)):
                if tokens[i] != "?":
                    # this SNP is observed
                    column_count[i - 1][0] += 1
                    if tokens[i] == "1":
                        # this SNP has the "alt"
                        column_count[i - 1][1] += 1
                        
    
    num_differences = 0
    for num_seqs, num_alt_allele in column_count:
        num_differences += num_alt_allele * (num_seqs - num_alt_allele)
        
    print("total aligned pairs: {}".format(total_aligned))
    print("total nucleotide differences: {}".format(num_differences))
    print("nucleotide diversity: {}".format(float(num_differences) / total_aligned))
    
        