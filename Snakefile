rule all:
    input:
        "example.accessions.lineages.csv"

rule download_wgs_acc2taxid:
    output:
        "nucl_wgs.accession2taxid.gz"
    shell:
        "curl -O -L ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_wgs.accession2taxid.gz"

rule download_gb_acc2taxid:
    output:
        "nucl_gb.accession2taxid.gz"
    shell:
        "curl -O -L ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/accession2taxid/nucl_gb.accession2taxid.gz"

rule download_taxdump:
    output:
        "taxdump/nodes.dmp",
        "taxdump/names.dmp"
    shell:
        "curl -L ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/taxdump.tar.gz | (mkdir -p taxdump && cd taxdump && tar xzvf -)"

rule make_taxid:
    input:
        "{name}.txt",
        "nucl_gb.accession2taxid.gz",
        "nucl_wgs.accession2taxid.gz"
    output:
        "{name}.txt.taxid"
    shell:
        "./make-acc-taxid-mapping.py {input[0]} {input[1]} {input[2]}"

rule make_lineage_csv:
    input:
        "{name}.txt.taxid",
        "taxdump/nodes.dmp",
        "taxdump/names.dmp"
    output:
        "{name}.lineages.csv"
    shell:
        "./make-lineage-csv.py taxdump/{{nodes.dmp,names.dmp}} {input[0]} -o {output}"

