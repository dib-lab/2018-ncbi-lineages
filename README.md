# Extracting taxonomic lineages from NCBI based on accessions

These tools are used to (among other things) create files for use with `sourmash lca index`, which creates LCA classification databases.  It starts by taking in a list of NCBI accession IDs, and ends with an output file format like so:

```
accession,taxid,superkingdom,phylum,class,order,family,genus,species,strain
AAAC01000001,191218,Bacteria,Firmicutes,Bacilli,Bacillales,Bacillaceae,Bacillus,Bacillus anthracis,
AABL01000001,73239,Eukaryota,Apicomplexa,Aconoidasida,Haemosporida,Plasmodiidae,Plasmodium,Plasmodium yoelii,
AABT01000001,285217,Eukaryota,Ascomycota,Eurotiomycetes,Eurotiales,Aspergillaceae,Aspergillus,Aspergillus terreus,
AABF01000001,209882,Bacteria,Fusobacteria,Fusobacteriia,Fusobacteriales,Fusobacteriaceae,Fusobacterium,Fusobacterium nucleatum,
```

### Snakestart: a snakemake workflow

Install snakemake, and run it:

```snakemake```

This will generate an output file `example.accessions.lineages.csv` based
on the input file `example.accessions.txt`. If you want to run it on your
own data, put a list of nucleotide accessions in a file `name.txt` and
run `snakemake name.lineages.csv` and it should all work. Note that snakemake
will download all of the necessary support files too!

### Quickstart: an example workflow

Get a list of accessions from a pile o' genbank genomes; here, we are using [sourmash](http://sourmash.readthedocs.io) to prepare an SBT and LCA database for further work, but you can do this without sourmash - all you need is the list of accessions.

#### Create a file with a lost of accessions

Download a bunch of genomes and get a list of accessions:
```
curl -L -o podar-genomes.tar.gz https://osf.io/8uxj9/download
tar xzf podar-genomes.tar.gz
head -1 {?,??}.fa | grep ^'>' | cut -c 2- > pg.acc
```

Extract taxids (see appendix to get the `nucl_*.gz` files):
```
./make-acc-taxid-mapping.py pg.acc nucl_{gb,wgs}*.gz
```

Build the lineage CSV:
```
./make-lineage-csv.py nodes.dmp names.dmp pg.acc.taxid -o podar-lineage.csv
```

...and done!

# Slightly more in-depth documentation

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

## Appendix 1: downloading files from NCBI

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

## Appendix 2: extracting accessions from a sourmash SBT

Download some genomes:
```
curl -L -o podar-genomes.tar.gz https://osf.io/8uxj9/download
tar xzf podar-genomes.tar.gz
```

Build an SBT and extract the accessions:
```
sourmash compute -k 31 --scaled=1000 {?,??}.fa --name-from-first
sourmash index pg {?,??}.fa.sig
./get-accessions-from-sbt.py pg -o pg.acc
```

Tada!

### Appendix 3: building an LCA database from a collection of signatures

Download some genomes and build signatures:
```
curl -L -o podar-genomes.tar.gz https://osf.io/8uxj9/download
tar xzf podar-genomes.tar.gz
sourmash compute -k 31 --scaled=1000 {?,??}.fa --name-from-first
```

Grab a lineage file (created as above):
```
curl -L -o podar-lineage.csv https://osf.io/4yhjw/download
```

Run `sourmash lca index`:
```
sourmash lca index podar-lineage.csv podar.lca.json {?,??}.fa.sig -C 3 --split-identifiers
```

Tada!

---

CTB 18.2.2018 

