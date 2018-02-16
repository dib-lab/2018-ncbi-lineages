# Extracting lineages from NCBI for use with sourmash lca

Code in:

https://github.com/dib-lab/2018-ncbi-lineages

# Step 1: create a file with a list of accessions

See, for example, `example.accessions.txt`, which contains a single accession: `NVAK01000095`.

# Step 2: build a mapping from accessions to taxid

Using the accession2taxid files available on the [NCBI FTP site](ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/), run `make-acc-taxid-mapping.py`:

```
./make-acc-taxid-mapping.py example.accessions.txt nucl_wgs.accession2taxid.gz
```

This will produce a file `example.accessions.txt.taxid` which contains the accession ID linked to the NCBI taxid.

# Step 3: extract full lineages from the NCBI taxdump

Using the `names.dmp` and `nodes.dmp` files from the [NCBI taxdump zip](ftp://ftp.ncbi.nih.gov/pub/taxonomy//taxdmp.zip), run `make-lineage-csv.py`:

```
./make-lineage-csv.py genbank/nodes.dmp.gz genbank/names.dmp.gz example.accessions.txt.taxid \
	-o example.lineage.csv
```

This will produce the final output file `example.lineage.csv` that is now `sourmash lca` compatible file:

```
accession,taxid,superkingdom,phylum,class,order,family,genus,species
NVAK01000095,1396,Bacteria,Firmicutes,Bacilli,Bacillales,Bacillaceae,Bacillus,Bacillus cereus
```