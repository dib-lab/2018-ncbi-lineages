#! /usr/bin/env python
from __future__ import print_function
import sys
import argparse
import csv

import ncbi_taxdump_utils 


want_taxonomy = ['superkingdom', 'phylum', 'class', 'order', 'family', 'genus', 'species']

def main():
    p = argparse.ArgumentParser()
    p.add_argument('nodes_dmp')
    p.add_argument('names_dmp')
    p.add_argument('acc_taxid_csv')
    p.add_argument('-o', '--output', type=argparse.FileType('wt'))
    args = p.parse_args()

    assert args.output

    taxfoo = ncbi_taxdump_utils.NCBI_TaxonomyFoo()

    taxfoo.load_nodes_dmp(args.nodes_dmp)
    taxfoo.load_names_dmp(args.names_dmp)

    r = csv.reader(open(args.acc_taxid_csv))
    w = csv.writer(args.output)

    w.writerow(['accession', 'taxid'] + want_taxonomy)

    count = 0
    for row in r:
        count += 1

        acc, taxid = row
        taxid = int(taxid)

        row = taxfoo.get_lineage(taxid, want_taxonomy)
        row.insert(0, taxid)
        row.insert(0, acc)

        w.writerow(row)

    print('output {} lineages'.format(count))


if __name__ == '__main__':
    main()
