"""
Utilities to deal with NCBI taxonomic foo.
"""

import gzip
import csv
import os
from pickle import dump, load
import collections


names_mem_cache = {}
nodes_mem_cache = {}


default_want_taxonomy = ['superkingdom', 'phylum', 'order', 'class', 'family', 'genus', 'species']


class NCBI_TaxonomyFoo(object):
    def __init__(self):
        self.child_to_parent = None
        self.node_to_info = None
        self.taxid_to_names = None
        self.accessions = None

    def load_nodes_dmp(self, filename, do_save_cache=True):
        if filename in nodes_mem_cache:
            self.child_to_parent, self.node_to_info = nodes_mem_cache[filename]
            return

        cache_file = filename + '.cache'
        if os.path.exists(cache_file):
            with xopen(cache_file, 'rb') as cache_fp:
                self.child_to_parent, self.node_to_info = load(cache_fp)
        else:
            self.child_to_parent, self.node_to_info = parse_nodes(filename)
            if do_save_cache:
                self.save_nodes_cache(cache_file)

        nodes_mem_cache[filename] = self.child_to_parent, self.node_to_info

    def save_nodes_cache(self, cache_file):
        with xopen(cache_file, 'wb') as cache_fp:
            dump((self.child_to_parent, self.node_to_info), cache_fp)

    def load_names_dmp(self, filename, do_save_cache=True):
        if filename in names_mem_cache:
            self.taxid_to_names = names_mem_cache[filename]
            return

        cache_file = filename + '.cache'
        if os.path.exists(cache_file):
            with xopen(cache_file, 'rb') as cache_fp:
                self.taxid_to_names = load(cache_fp)
        else:
            self.taxid_to_names = parse_names(filename)
            self.save_names_cache(cache_file)

        names_mem_cache[filename] = self.taxid_to_names

    def save_names_cache(self, cache_file):
        with xopen(cache_file, 'wb') as cache_fp:
            dump(self.taxid_to_names, cache_fp)

    def load_accessions_csv(self, filename):
        self.accessions = load_genbank_accessions_csv(filename)

    # get taxid
    def get_taxid(self, acc):
        # @CTB hack hack split off NZ from accession
        if acc.startswith('NZ_'):
            acc = acc[3:]

        info = self.accessions.get(acc)
        if not info:
            return None

        taxid = info['taxid']
        taxid = int(taxid)
        return taxid

    # code to find the last common ancestor from a set of taxids
    def find_lca(self, taxid_set):
        # empty? exit.
        if not taxid_set:
            return 1

        # get the first full path
        taxid_set = set(taxid_set)        # make a copy
        taxid = taxid_set.pop()
        path = []
        while taxid != 1:
            path.insert(0, taxid)
            taxid = self.child_to_parent.get(taxid, 1)   # @CTB reexamine

        # find the first shared taxid in each follow-on path
        while taxid_set:
            taxid = taxid_set.pop()

            path2 = []
            while taxid != 1:
                if taxid in path:
                    path2.insert(0, taxid)
                taxid = self.child_to_parent.get(taxid, 1)

            path = path2

        if path:
            return path[-1]
        return 1

    def is_strain(self, taxid):
        if self.get_taxid_rank(taxid) == 'no rank':
            parent = self.get_taxid_parent(taxid)
            if self.get_taxid_rank(parent) == 'species':
                return True
        return False


    def get_taxid_name(self, taxid):
        if taxid not in self.node_to_info:
            return None

        name = self.taxid_to_names[taxid][0]
        return name

    def get_taxid_rank(self, taxid):
        if taxid not in self.node_to_info:
            return None

        rank = self.node_to_info[taxid][0]
        return rank

    def get_taxid_parent(self, taxid):
        return self.child_to_parent.get(taxid, None)

    def get_lineage_as_taxids(self, taxid):
        """
        Extract the text taxonomic lineage in order (kingdom on down).
        """
        taxid = int(taxid)
        
        lineage = []
        while 1:
            lineage.insert(0, taxid)
            taxid = self.get_taxid_parent(taxid)
            if taxid is None:
                raise ValueError('cannot find taxid {}'.format(taxid))

            if taxid == 1:
                break

        return lineage
        
    def get_lineage(self, taxid, want_taxonomy=None):
        """
        Extract the text taxonomic lineage in order (kingdom on down).
        """
        taxid = int(taxid)

        lineage = []
        while 1:
            if taxid not in self.node_to_info:
                print('cannot find taxid {}; quitting.'.format(taxid))
                break
            rank = self.get_taxid_rank(taxid)
            name = self.get_taxid_name(taxid)
            if self.is_strain(taxid): # NCBI reports strain as 'no rank'...
                rank = 'strain'
            if not want_taxonomy or rank in want_taxonomy:
                lineage.insert(0, name)
            taxid = self.get_taxid_parent(taxid)
            if taxid == 1:
                break

        return lineage


    def get_lineage_as_dict(self, taxid, want_taxonomy=None):
        """
        Extract the text taxonomic lineage in order (kingdom on down);
        return in dictionary.
        """
        taxid = int(taxid)

        lineage = {}
        while 1:
            if taxid not in self.node_to_info:
                print('cannot find taxid {}; quitting.'.format(taxid))
                break

            rank = self.get_taxid_rank(taxid)
            name = self.get_taxid_name(taxid)

            if self.is_strain(taxid): # NCBI reports strain as 'no rank'...
                rank = 'strain'
            if not want_taxonomy or rank in want_taxonomy:
                lineage[rank] = name
            taxid = self.get_taxid_parent(taxid)
            if taxid == 1:
                break

        return lineage

    def get_lowest_lineage(self, taxids, want_taxonomy):
        """\
        Find the taxid of the lowest taxonomic rank consonant with a bunch of
        taxids.
        """

        # across all taxids, what ranks are found?
        ranks_found = collections.defaultdict(set)
        for taxid in taxids:
            lineage = self.get_lineage_as_taxids(taxid)

            for l_taxid in lineage:
                rank = self.get_taxid_rank(l_taxid)
                ranks_found[rank].add(l_taxid)

        # now, extract the lowest one:
        last_taxid = [1]
        for rank in want_taxonomy:
            if ranks_found.get(rank):
                last_taxid = ranks_found[rank]
                        
        assert len(last_taxid) == 1
        taxid = min(last_taxid)       # get only element in set
        return taxid

        
    def get_lineage_first_disagreement(self, taxids, want_taxonomy):
        """\
        Find the first taxonomic rank where the taxids actually disagree.

        Returns (None, None) if no disagreement.
        This will ignore situations where one taxid is the ancestor of another.
        """
        # across all taxids, what ranks are found?
        ranks_found = collections.defaultdict(set)
        for taxid in taxids:
            try:
                lineage = self.get_lineage_as_taxids(taxid)
            except ValueError:
                print('ERROR in lineage for taxid', taxid)
                raise

            for l_taxid in lineage:
                rank = self.get_taxid_rank(l_taxid)
                ranks_found[rank].add(l_taxid)

        # find first place where there are multiple names at a given rank
        last_rank = want_taxonomy[0]
        for rank in want_taxonomy:
            if len(ranks_found.get(rank, [])) > 1:
                return (last_rank, list(ranks_found[last_rank])[0], ranks_found[rank])
            last_rank = rank

        return (None, None, None)


### internal utility functions
def xopen(filename, mode):
    if filename.endswith('.gz'):
        return gzip.open(filename, mode)
    return open(filename, mode)

def parse_nodes(filename):
    "Parse the NCBI nodes_dmp file."
    child_to_parent = dict()
    node_to_info = dict()

    with xopen(filename, 'rt') as fp:
        for n, line in enumerate(fp):
            x = line.split('\t|\t')

            node_id, parent_node_id, rank, embl, div_id, div_flag, gencode, mgc_inherit, mgc_flag, mgc_id, hidden_flag, subtree_flag, comments = x

            node_id = int(node_id)
            parent_node_id = int(parent_node_id)

            child_to_parent[node_id] = parent_node_id
            node_to_info[node_id] = rank, embl, div_id, div_flag, comments

    return child_to_parent, node_to_info


def parse_names(filename):
    """
    Parse an NCBI names.dmp file.
    """
    taxid_to_names = dict()
    with xopen(filename, 'rt') as fp:
        for n, line in enumerate(fp):
            line = line.rstrip('\t|\n')
            x = line.split('\t|\t')

            taxid, name, uniqname, name_class = x
            taxid = int(taxid)

            if name_class == 'scientific name':
                taxid_to_names[taxid] = (name, uniqname, name_class)

    return taxid_to_names


def load_genbank_accessions_csv(filename):
    """
    Load a file containing genbank accession -> taxid + lineage string.

    See https://github.com/dib-lab/2017-ncbi-taxdump for scripts to create
    this file from a large collection of sequences.
    """
    # load the genbank CSV (accession -> lineage)
    print('loading genbank accession -> lineage info')
    with xopen(filename, 'rt') as fp:
        accessions = {}
        for row in csv.DictReader(fp, fieldnames=['acc', 'taxid', 'lineage']):
            acc = row['acc']
            accessions[acc] = row

    return accessions
