path = {
    "bracken_path": "/home/bayegy/pipelines/metagenome/softwares/bracken/src/est_abundance.py",
    "bracken_database": "/home/bayegy/Databases/kraken_bracken/database150mers.kmer_distrib",
    "fmap_home": "/home/bayegy/pipelines/metagenome/softwares/FMAP/",
    "bayegy_home": "/home/bayegy/pipelines/metagenome/Bayegy/",
    "megahit_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/megahit",
    # conda install -c bioconda cd-hit # cd-hit installed by conda does not suport multi-threading
    "cdhit_path": "/home/bayegy/pipelines/metagenome/softwares/cd-hit-v4.8.1-2019-0228/cd-hit-est",
    "circos_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/circos",
    "circos_etc": "/home/bayegy/pipelines/metagenome/miniconda2/pkgs/circos-0.69.8-0/etc",
    "ncbi_taxaID_path": "/home/bayegy/Databases/kraken_bracken/taxid2OTU_ranks.txt",
    "quast_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/quast.py",
    "kraken2_database": "/home/bayegy/Databases/kraken_bracken/",
    "emapper_database": "/home/bayegy/Databases/emapper/eggnog",
    "cazy_database": "/home/bayegy/Databases/diamond/CAZyDB.07312018.dmnd",
    "humann2_home": "/home/bayegy/pipelines/metagenome/miniconda2/bin/",
    # conda install humann2 -c biobackery # do not use bioconda channel
    "humann2_protein_database": "/home/bayegy/Databases/humann2/uniref90_full",
    "humann2_nucleotide_database": "/home/bayegy/Databases/humann2/chocophlan_full",
    "humann2_utility_mapping": "/home/bayegy/Databases/humann2/utility_mapping",
    "map_conf": "/home/bayegy/Databases/colormap",
    "kneaddata_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/kneaddata",
    "trimmomatic_home": "/home/bayegy/pipelines/metagenome/miniconda2/pkgs/trimmomatic-0.39-1/share/trimmomatic-0.39-1",
    "bowtie2_home": "/home/bayegy/pipelines/metagenome/miniconda2/bin/",
    "metaphlan2_home": "/home/bayegy/pipelines/metagenome/miniconda2/bin/",
    "metaphlan2_database": "/home/bayegy/pipelines/metagenome/miniconda2/bin/databases",
    "diamond_home": "/home/bayegy/pipelines/metagenome/miniconda2/bin/",
    "salmon_path": "/home/bayegy/pipelines/metagenome/softwares/salmon-latest_linux_x86_64/bin/salmon",
    "kraken2_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/kraken2",
    "adapters_path": "/home/bayegy/pipelines/metagenome/MetaGenome/data/adaptor_Illumina.fa",
    # conda install emboss
    "transeq_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/transeq",
    # conda install -c bioconda eggnog-mapper
    "emapper_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/emapper.py",
    "fastqc_home": "/home/bayegy/pipelines/metagenome/miniconda2/bin/",
    "python3_path": "/usr/bin/python3",
    "R_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/Rscript",
    "perl_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/perl",
    "qiime2_home": "/home/bayegy/pipelines/metagenome/miniconda2/envs/qiime2-2019.10",
    "lefse_pylib_home": "/home/bayegy/pipelines/metagenome/miniconda2/share/lefse-1.0.8.post1-1",
    "lefse_rlib_home": "/home/bayegy/pipelines/metagenome/miniconda2/lib/R/library",
    "lefse_py_home": "/home/bayegy/pipelines/metagenome/miniconda2/bin/",
    "prodigal_path": "/home/bayegy/pipelines/metagenome/miniconda2/bin/prodigal",
    # sudo apt-get install ttf-mscorefonts-installer #安装字体
    # /etc/ImageMagick-6/policy.xml replace the value of PDF rights to "read|write"
    # do not use conda to install salmon, it's too old
    # sudo apt-get install mpich #cd-hit nedd this
    # humann2 installed by bioconda is too old!
    # sudo apt-get install libopenblas-dev # to solve 'libopenblas.so.0: cannot open shared object file'

}

memery_needs = {
    "kneaddata": 160,
    "kraken2": 70,
    "humann2": 45,
    "fmap": 30,
    "salmon": 1000,
    "megahit": 200,
    "prodigal": 50,
    "cdhit": 100,
    "diamond_cazy": 100,
    "diamond_card": 100,
    "emapper": 100,
}

memery = 2000

threads = 180

hosts = 2

use_sge = True

sge_pe = "smp"

sge_queue = "metagqueue"

max_workers = {
    "kneaddata": 6,
    "kraken2": 6,
    "humann2": 6,
    "fmap": 12,
    "salmon": 2,
    "megahit": 6,
    "prodigal": 30,
    "cdhit": 1,
    "diamond_cazy": 10,
    "diamond_card": 10,
    "emapper": 20,
}


each = {
    "prodigal": 30,
    "cdhit": 6,
    "diamond_cazy": 2,
    "diamond_card": 2,
    "emapper": 2,
}
