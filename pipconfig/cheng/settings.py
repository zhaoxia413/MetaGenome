path = {
    "bracken_path": "/home/cheng/softwares/bracken/Bracken/src/est_abundance.py",
    "bracken_database": "/home/cheng/Databases/Dec_2019_4_multitaxa/database150mers.kmer_distrib",
    "fmap_home": "/home/cheng/softwares/FMAP/",
    "cii_home": "/home/cheng/pipelines/CII_meta/",
    "bayegy_home": "/home/cheng/pipelines/Bayegy/",
    "de_host_home": "/home/cheng/pipelines/IlluminaPipeline/SE_map_host_subtract/",
    "merge_se_home": "/home/cheng/pipelines/IlluminaPipeline/PE_assembly/",
    "megahit_path": "/home/cheng/softwares/megahit/megahit/megahit",
    # "cdhit_path": "/home/cheng/softwares/cd-hit-v4.8.1-2019-0228/cd-hit-est",
    "cdhit_path": "/home/cheng/softwares/cd-hit-v4.8.1-2019-0228/cd-hit-est",
    "circos_path": "/media/cheng/disk1/huty/softwares/circos-0.69-9/bin/circos",
    "circos_etc": "/home/cheng/huty/softwares/circos-0.69-9/etc",
    "ncbi_taxaID_path": "/home/cheng/Databases/taxid2OTU_ranks.txt",
    "quast_path": "/home/cheng/softwares/quast/quast-5.0.2/quast.py",
    "kraken2_database": "/home/cheng/Databases/Dec_2019_4_multitaxa/",
    "emapper_database": "/home/cheng/Databases/eggnog/",
    "cazy_database": "/home/cheng/Databases/protein/CAZy/CAZyDB.07312018.dmnd",
    "humann2_home": "/home/cheng/softwares/miniconda2/bin/",
    "humann2_protein_database": "/home/cheng/Databases/humann2/uniref90_full",
    "humann2_nucleotide_database": "/home/cheng/Databases/humann2/chocophlan_full",
    "humann2_utility_mapping": "/home/cheng/Databases/humann2/utility_mapping",
    "metaphlan2_database": "/home/cheng/softwares/miniconda2/bin/metaphlan_databases",
    "map_conf": "/home/cheng/Databases/map/",
    "kneaddata_path": "/home/cheng/miniconda2/bin/kneaddata",
    "trimmomatic_home": "/home/cheng/pipelines/Genome/softwares/Trimmomatic-0.39/",
    "bowtie2_home": "/home/cheng/softwares/miniconda2/bin/",
    "metaphlan2_home": "/home/cheng/softwares/miniconda2/bin/",
    "diamond_home": "/home/cheng/softwares/miniconda2/bin/",
    "salmon_path": "/home/cheng/softwares/salmon-latest_linux_x86_64/bin/salmon",
    "kraken2_path": "/home/cheng/softwares/kraken2/kraken2/kraken2",
    "adapters_path": "/home/cheng/pipelines/MetaGenome/data/adaptor_Illumina.fa",
    "transeq_path": "/home/cheng/softwares/miniconda2/bin/transeq",
    "emapper_path": "/home/cheng/softwares/miniconda2/bin/emapper.py",
    "fastqc_home": "/home/cheng/softwares/fastqc/FastQC/",
    "python3_path": "/usr/bin/python3",
    "R_path": "/usr/bin/Rscript",
    "perl_path": "/usr/bin/perl",
    "qiime2_home": "/home/cheng/miniconda2/envs/qiime2-2019.4/",
    "lefse_pylib_home": "/home/cheng/softwares/miniconda2/share/lefse-1.0.8.post1-1",
    "lefse_rlib_home": "/home/cheng/softwares/miniconda2/envs/lefse/lib/R/library/",
    "lefse_py_home": "/home/cheng/softwares/miniconda2/envs/lefse/bin",
    "prodigal_path": "/home/cheng/softwares/miniconda2/bin/prodigal",
}

memery_needs = {
    "kneaddata": 150,
    "kraken2": 70,
    "humann2": 45,
    "fmap": 40,
    "salmon": 250,
    "megahit": 100,
    "prodigal": 50,
    "cdhit": 400,
    "diamond_cazy": 400,
    "diamond_card": 400,
    "emapper": 400,
}


memery = 500

threads = 63

hosts = 1

use_sge = False

sge_pe = "smp"

sge_queue = "queue1"

max_workers = {
    "kneaddata": 5,
    "kraken2": 6,
    "humann2": 5,
    "fmap": 10,
    "salmon": 2,
    "megahit": 4,
    "prodigal": 10,
    "cdhit": 1,
    "diamond_cazy": 1,
    "diamond_card": 1,
    "emapper": 1,
}

each = {
    "prodigal": 30,
    "cdhit": 6,
    "diamond_cazy": 2,
    "diamond_card": 2,
    "emapper": 2,
}
