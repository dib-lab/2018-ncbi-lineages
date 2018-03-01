import os
import argparse
import pandas as pd


def parse_assembly_summary(summaryFile, outName):
    """
    Parse an NCBI assembly summary file to create a csv with accession number, version, and tax id.
    e.g. e.g. https://ftp.ncbi.nih.gov/genomes/genbank/invertebrate/assembly_summary.txt 
    """
    assembInfo = pd.read_csv(summaryFile, header=1, sep='\t')
    outF = outName + '_parsed_acc2taxid.txt'
    assembInfo["accession"] = assembInfo["# assembly_accession"].str.split('.', n=1,expand=True)[0]
    assembInfo.rename(columns={'# assembly_accession':'accession.version'}, inplace=True)
    imp_cols = ['accession','accession.version', 'taxid'] #, 'species_taxid', 'organism_name']
    #write out relevant colums
    assembInfo.to_csv(outF, columns=imp_cols, index=False, sep='\t')


if __name__ == '__main__':
    """
    """
    psr = argparse.ArgumentParser()
    psr.add_argument('-o', '--outName', default= os.getcwd())
    psr.add_argument('-a', '--assemblySummary')
    args = psr.parse_args()
    parse_assembly_summary(args.assemblySummary, args.outName)

