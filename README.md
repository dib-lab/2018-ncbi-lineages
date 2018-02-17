# Extracting taxonomic lineages from NCBI based on accessions

This workflow is used to (among other things) create files for use with `sourmash lca index`, which creates LCA classification databases.  It starts by taking in a list of NCBI accession IDs, and ends with an output file format like so:

```
accession,taxid,superkingdom,phylum,class,order,family,genus,species,strain
AAAC01000001,191218,Bacteria,Firmicutes,Bacilli,Bacillales,Bacillaceae,Bacillus,Bacillus anthracis,
AABL01000001,73239,Eukaryota,Apicomplexa,Aconoidasida,Haemosporida,Plasmodiidae,Plasmodium,Plasmodium yoelii,
AABT01000001,285217,Eukaryota,Ascomycota,Eurotiomycetes,Eurotiales,Aspergillaceae,Aspergillus,Aspergillus terreus,
AABF01000001,209882,Bacteria,Fusobacteria,Fusobacteriia,Fusobacteriales,Fusobacteriaceae,Fusobacterium,Fusobacterium nucleatum,
```

## Step 1: create a file with a list of accessions

See, for example, `example.accessions.txt`, which contains a single accession: `NVAK01000095`. This file can be produced from a sourmash SBT using the `get-accessions-from-sbt.py` script -- e.g.,

```
./get-accessions-from-sbt.py ../genbank-k31.sbt.json -o genbank.acc.txt
```

which produces a file formatted like so,

```
CODD02000001.1 Streptococcus pneumoniae genome assembly 7622_4#12, scaffold LE4019_contig_100, whole genome shotgun sequence
JSCH01000001.1 Acinetobacter baumannii strain 2011BJAB4 contig_1, whole genome shotgun sequence
KK041881.1 Staphylococcus aureus F77917 genomic scaffold adFHh-supercont1.1, whole genome shotgun sequence
```
(The next step will ignore everything past the first field in each line.)

## Step 2: build a mapping from accessions to taxid

Using the accession2taxid files available on the [NCBI FTP site](ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/), run `make-acc-taxid-mapping.py`:

```
./make-acc-taxid-mapping.py example.accessions.txt nucl_wgs.accession2taxid.gz
```

This will produce a file `example.accessions.txt.taxid` which contains the accession ID linked to the NCBI taxid, e.g.:

```
NVAK01000095,1396
```

## Step 3: extract full lineages from the NCBI taxdump

Using the `names.dmp` and `nodes.dmp` files from the [NCBI taxdump zip](ftp://ftp.ncbi.nih.gov/pub/taxonomy//taxdmp.zip), run `make-lineage-csv.py`:

```
./make-lineage-csv.py genbank/nodes.dmp.gz genbank/names.dmp.gz example.accessions.txt.taxid \
	-o example.lineage.csv
```

This will produce the final output file `example.lineage.csv` that is now a `sourmash lca` compatible file:

```
accession,taxid,superkingdom,phylum,class,order,family,genus,species
NVAK01000095,1396,Bacteria,Firmicutes,Bacilli,Bacillales,Bacillaceae,Bacillus,Bacillus cereus
```

## Appendix: downloading files from NCBI

The following commands will put the necessary files from NCBI in the `genbank/` directory.

```
mkdir genbank/

cd genbank/

curl -L -O ftp://ftp.ncbi.nih.gov/pub/taxonomy//taxdmp.zip
unzip taxdmp.zip nodes.dmp names.dmp
rm taxdmp.zip

curl -L -O ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz
curl -L -O ftp://ftp.ncbi.nih.gov/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.gz
```