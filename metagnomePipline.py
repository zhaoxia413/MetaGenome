import os
import time
from pyutils.tools import split_list, parse_premap
import json
import re
from visualizeAll import VisualizeAll
from mapInfo import MapInfo
import pandas as pd
from pyutils.tools import time_counter
from systemMixin import SystemMixin
import numpy as np
from pipconfig import settings
from lxml import html
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from queue import Queue
import uuid


class RawDataNotPairedError(Exception):
    pass


class PathError(Exception):
    pass


class MetagenomePipline(SystemMixin):
    """
    arguments:
        pre_mapping_file: The first column of pre_mapping_file should be smaple id in raw fastq files, the last column of pre_mapping_file should be revised id (or the same) of samples.

        categories: Categories seprated by ',' , optional, if not passed, the categories names should have the pattern of 'Category.*'

        host_type: Will control the de_host step.

        run_size: Control the max number of jobs submitted to sge each time

        raw_fqs_dir: Directory where the raw fastq file weres stored

        sample_regex: Regular expression to match sample id (contained by brackets)

        forward_regex: Regular expression to match forward fastq files

        reverse_regex: Regular expression to match reverse fastq files

        out_dir: Where to store the results

    sample usage:

    from metagnomePipline import MetagenomePipline
    m =MetagenomePipline('/home/cheng/Projects/rll_testdir/1.rawdata/','/home/cheng/Projects/rll_testdir/mapping_file.txt',out_dir="/home/cheng/Projects/rll_testdir/")
    m.run()
    """

    def __init__(self, raw_fqs_dir, pre_mapping_file, categories=False, host_db="/home/cheng/Databases/hg38/hg38", sample_regex="(.+)_.*_[12]\.fq\.?g?z?", forward_regex="_1\.fq\.?g?z?$", reverse_regex="_2\.fq\.?g?z?$", out_dir='./', base_on_assembly=False, exclude='none'):
        self.context = dict()

        self.set_path(force=True,
                      out_dir=out_dir,
                      raw_dir=out_dir + '/raw_dir',
                      salmon_out=out_dir + '/salmon_out',
                      kneaddata_out=out_dir + '/kneaddata_out',
                      kraken2_out=out_dir + '/Kraken2',
                      amr_out=out_dir + '/AMR',
                      humann2_out=out_dir + '/Metagenome/Humann/',
                      fmap_out=out_dir + '/FMAP/',
                      assembly_out=out_dir + "/Assembly_out",
                      metaphlan_out=out_dir + "/Metagenome/Metaphlan",
                      report_out=out_dir + "/Report",
                      )

        self.set_attr(base_on_assembly=base_on_assembly,
                      mapping_file=self.out_dir + '/mapping_file.txt',
                      host_db=host_db,
                      exclude=exclude,
                      base_dir=os.path.dirname(__file__) + '/',
                      **self.get_attrs(settings))

        if not hasattr(self, 'tmp_dir'):
            self.set_path(force=True, tmp_dir=os.path.join(
                '/dev/shm/', str(uuid.uuid1()) + '_metagenomepipeline_tmp_dir'))

        self.set_path(force=False, **self.path)
        self.parsed_map = parse_premap(raw_fqs_dir, pre_mapping_file, forward_regex, reverse_regex, sample_regex)
        self.fq_info = self.parsed_map['fastq'].values
        self.new_ids = list(self.parsed_map['map']['#SampleID'].values)
        self.new_ids.sort()
        self.parsed_map['map'].to_csv(self.mapping_file, sep='\t', index=False)
        self.categories = categories if categories else ','.join(
            [g for g in self.parsed_map['map'].columns if not g.find('Category') == -1])
        print("The detected categories are: \n\n{}\n".format(self.categories))

        self.raw_pattern = "%s/{sample_id}_{direction}.fq" % (self.raw_dir)
        self.raw_list = self.paired_data(self.raw_pattern, 5)
        self.clean_paired_pattern = "%s/{sample_id}_R1_kneaddata_paired_{direction_num}.fastq" % (self.kneaddata_out)
        self.clean_paired_r1_list = self.map_list(self.clean_paired_pattern, 10, use_direction='R1')
        self.clean_paired_list = self.paired_data(self.clean_paired_pattern, 5)
        self.kracken2_reports_pattern = "%s/{sample_id}.report" % (self.kraken2_out)
        self.kracken2_reports_list = self.map_list(self.kracken2_reports_pattern, use_direction='R1')
        self.qc_stats_queue = Queue()
        global running_list
        running_list = self.out_dir + '.running_list'
        global tmp_dir
        tmp_dir = self.tmp_dir

    def format_raw(self):
        for fq_path, new_id, direction in self.fq_info:
            formated_fq = self.raw_pattern.format(sample_id=new_id, direction=direction)
            if not os.path.exists(formated_fq):
                if fq_path.endswith('.gz'):
                    print("Unzip file {}...".format(fq_path))
                    os.system("gunzip {}".format(fq_path))
                    fq_path = fq_path.rstrip('.gz')
                os.system("ln -s {} {}".format(fq_path, formated_fq))

    def map_list(self, pattern=False, each=False, use_direction="both"):
        out = []
        for fq_path, new_id, direction in self.fq_info:
            ele = pattern.format(sample_id=new_id, direction=direction, direction_num=re.search(
                "\d$", direction).group()) if pattern else [new_id, direction]
            if direction == "R2" and (use_direction == "both" or use_direction == "R2"):
                out.append(ele)
            elif direction == "R1" and (use_direction == "both" or use_direction == "R1"):
                out.append(ele)
        out.sort()
        return split_list(out, each) if each else out

    def paired_data(self, pattern, each=False):
        r1 = self.map_list(pattern=pattern, each=False, use_direction="R1")
        r2 = self.map_list(pattern=pattern, each=False, use_direction="R2")
        if not len(r1) == len(r2):
            raise RawDataNotPairedError("The file number of Reads1 and Reads2 is not equal")
        out = np.array([r1, r2]).T.tolist()
        return split_list(out, each) if each else out

    @staticmethod
    def mirror_move(source, target):
        for root, dirs, files in os.walk(source):
            target_dir = root.replace(source.rstrip('/'), target, 1)
            if target_dir.startswith('~'):
                raise PathError("'~' is illegal in path!")
            if not os.path.exists(target_dir):
                print("Making directory: {}".format(target_dir))
                os.system("mkdir -p '{}'".format(target_dir))
            for fl in files:
                source_file = os.path.join(root, fl)
                os.system("mv '{}' '{}'".format(source_file, target_dir))

    def synchronize(func):
        """
        对于被修饰的函数：fq_list参数值应是单个fq文件的路径（或路径对）
        对于最终函数：fq_list参数是多个fq文件路径的二(至少)维数组(list)
        """

        def wfunc(*args, fq_list, first_check=10, shift_results=False, **kwargs):
            global tmp_dir
            print("######################Running " + str(func))
            start_time = time.time()
            for fqs in fq_list:
                for fq in fqs:
                    func(*args, fq_list=fq, **kwargs)
                time.sleep(first_check * 60)
                while True:
                    if not list(os.popen("qstat")):
                        break
                    time.sleep(60)
                if shift_results:
                    MetagenomePipline.mirror_move(tmp_dir, shift_results)
                if os.listdir(tmp_dir):
                    os.system("rm -r {}/*".format(tmp_dir))
            end_time = time.time()
            time_used = (end_time - start_time) / 60
            print("######################" + str(func) + " done; time used: {} min".format(time_used))
        return wfunc

    def homized_cmd(self, cmd, home=False):
        home = home or self.base_dir
        return "cd {}&&{}".format(home, cmd)

    def parse_fq_list(self, fq_list):
        if isinstance(fq_list, list):
            return {
                "r1": fq_list[0],
                "r2": fq_list[1],
                "sample": os.path.basename(fq_list[0]).split('_')[0]
            }
        else:
            return {
                "r1": fq_list,
                "sample": os.path.basename(fq_list).split('_')[0]
            }

    @synchronize
    def run_kneaddata(self, fq_list, threads=10, mem=20):
        self.system("""
echo '{kneaddata_path} -i {r1} -i {r2} -o {kneaddata_out} -v -db {host_db} \
 --remove-intermediate-output  -t {threads} --run-fastqc-start --run-fastqc-end \
 --trimmomatic {trimmomatic_home} --trimmomatic-options "ILLUMINACLIP:{adapters_path}:2:30:10 SLIDINGWINDOW:4:20 MINLEN:50" --max-memory {mem}g \
 --bowtie2 {bowtie2_home} \
 --fastqc  {fastqc_home}' \
 | qsub -V -N {sample} -cwd -l h_vmem={mem}G -o {kneaddata_out} -e {kneaddata_out} -pe smp {threads}
            """, **self.parse_fq_list(fq_list), kneaddata_out=self.tmp_dir, threads=threads, mem=mem)

    @synchronize
    def run_kraken2(self, fq_list, threads=2, mem=70):
        self.system("""
echo '{kraken2_path} --db {kraken2_database} --threads {threads} --confidence 0.2 \
 --report {kraken2_out}/{sample}.report --paired {r1} {r2}' \
  | qsub -S /bin/bash -V -N {sample} -l h_vmem={mem}G -o {kraken2_out} -e {kraken2_out} -pe smp {threads}
            """, **self.parse_fq_list(fq_list), threads=threads, mem=mem)

    def run_bracken(self):
        global running_list
        bracken_list = [l + '.bracken' for l in self.kracken2_reports_list]
        for report in self.kracken2_reports_list:
            self.system(
                "python2 {bracken_path} -i {report} -k {bracken_database} -l S -o {report}.bracken", report=report)
        with open(running_list, 'w') as f:
            f.write('\n'.join(bracken_list))
        os.system(
            self.homized_cmd("perl Braken_to_OTUtable.pl {} {}".format(self.ncbi_taxaID_path, running_list)))

    def clean_header(self, tb_name, pattern, skip=[]):
        df = pd.read_csv(tb_name, sep='\t')
        df.columns = [re.sub(pattern, '', c) for c in df.columns]
        df.drop(index=skip).to_csv(tb_name, sep="\t", index=False)

    def join_metaphlan(self):
        tb_name = self.metaphlan_out + '/All.Metaphlan2.profile.txt'
        self.system(
            "python2 {base_dir}/merge_metaphlan_tables.py {humann2_out}/*profile.txt > {tb_name}", tb_name=tb_name)
        self.clean_header(tb_name, pattern='_R1.metaphlan.profile$', skip=[0])

    @synchronize
    def run_humann2(self, fq_list, threads=2, mem=40):
        self.system("""
echo '{humann2_home}/humann2 --input {r1} \
  --bowtie2 {bowtie2_home} --metaphlan {metaphlan2_home} --diamond {diamond_home} \
  --protein-database {humann2_protein_database} --nucleotide-database {humann2_nucleotide_database} \
  --threads {threads} --memory-use  maximum \
  --output-basename {sample} \
  --output {humann2_out} \
  --remove-temp-output' \
  | qsub -S /bin/bash -V -N {sample} -l h_vmem={mem}G -pe smp {threads} -o {humann2_out} -e {humann2_out} -j y
            """, **self.parse_fq_list(fq_list), threads=threads, mem=mem)

    def join_humann(self):
        self.system('''
ln -s {humann2_out}/*/*genefamilies.tsv {humann2_out}/*/*pathabundance.tsv {humann2_out}/
{humann2_home}/humann2_join_tables -i {humann2_out}/ -o {humann2_out}/RPK.All.UniRef90.genefamilies.tsv --file_name genefamilies.tsv
{humann2_home}/humann2_join_tables -i {humann2_out}/ -o {humann2_out}/RPK.All.Metacyc.pathabundance.tsv --file_name pathabundance.tsv''')
        self.clean_header(self.out_dir + "Metagenome/Humann/RPK.All.UniRef90.genefamilies.tsv",
                          pattern='_.*Abundance-RPKs$')
        self.clean_header(self.out_dir + "Metagenome/Humann/RPK.All.Metacyc.pathabundance.tsv",
                          pattern='_.*Abundance$')

    def set_fmap_db(self, database):
        with open(self.fmap_home + '/FMAP_data/database', 'w') as f:
            f.write(database)

    @synchronize
    def run_fmap(self, fq_list, threads=4, mem=24):
        self.system("""
echo 'perl {fmap_home}/FMAP_mapping.pl -p {threads} {r1} > {fmap_out}/{sample}.mapping.txt' | \
 qsub -V -N {sample} -cwd -l h_vmem={mem}G -o {fmap_out} -e {fmap_out} -pe smp {threads}
            """, **self.parse_fq_list(fq_list))

    def quantify_fmap(self, all_name="all.txt", print_definition=False):
        p = "" if print_definition else "-n"
        for new_id in self.new_ids:
            self.system(
                "perl {fmap_home}/FMAP_quantification.pl {fmap_out}/{sample}.mapping.txt > {fmap_out}/{sample}.abundance.txt", sample=new_id)
        args = [
            "{sample}={fmap_out}/{sample}.abundance.txt".format(sample=new_id, fmap_out=self.fmap_out) for new_id in self.new_ids]
        self.system("perl {fmap_home}/FMAP_table.pl {p} {args} > {fmap_out}/{all_name}",
                    p=p, args=args, all_name=all_name)

    def fmap_wrapper(self, fq_list, run_type="KEGG", threads=4, mem=10):
        fmap_db = {
            "KEGG": "orthology_uniref90_2_2157_4751.20190412161853",
            "AMR": "protein_fasta_protein_homolog_model_cleaned",
            "ARDB": "ARDB.20180725064354",
            "MGE": "MGEs_FINAL_99perc_trim"
        }
        self.set_fmap_db(fmap_db[run_type])
        self.run_fmap(fq_list=fq_list, threads=threads, mem=mem)
        self.quantify_fmap(all_name="All.{}.abundance_unstratified.tsv".format(run_type))

    def run_assembly(self, threads=50):
        self.system(
            "{megahit_path} -1 {r1_list} -2 {r2_list} --min-contig-len 1000 -t {threads} -o {assembly_out}",
            r1_list=','.join(self.map_list(self.clean_paired_pattern, use_direction="R1")),
            r2_list=','.join(self.map_list(self.clean_paired_pattern, use_direction="R2")),
            threads=threads
        )

        self.system(
            """
cd {assembly_out}
prodigal -i final.contigs.fa -a final.contigs.fa.faa -d final.contigs.fa.fna  -f gff -p meta -o final.contigs.fa.gff
{cdhit_path} -i final.contigs.fa.fna -c 0.9 -G 0 -aS 0.9 -g 1 -d 0 -M 0 -o NR.nucleotide.fa -T 0
grep '>' NR.nucleotide.fa > NR.nucleotide.fa.header
{cmd}
Rscript ORF_header_summary.R -i {assembly_out}""",
            cmd=self.homized_cmd(
                "perl ORF_generate_input_stats_file.pl {assembly_out}/NR.nucleotide.fa.header".format(**self.context)),
        )

    def run_quast(self):
        self.system("python2 {quast_path} -o {assembly_out}/quast_results/  {assembly_out}/final.contigs.fa")

    def create_gene_db(self, threads=7):
        self.system('''
{transeq_path} -sequence {assembly_out}/NR.nucleotide.fa -outseq {assembly_out}/NR.protein.fa -trim Y
sed -i 's/_1 / /' {assembly_out}/NR.protein.fa
{salmon_path} index -t {assembly_out}/NR.nucleotide.fa -p {threads} -k 31 -i {assembly_out}/salmon_index''', threads=threads)

    @synchronize
    def quant_gene(self, fq_list, threads=7, mem=80):
        self.system("""
echo '{salmon_path} quant -i {assembly_out}/salmon_index -l A -p {threads} --meta -1 {r1} -2 {r2} -o {salmon_out}/{sample}.quant' \
| qsub -V -N {sample} -cwd -l h_vmem={mem}G -o {salmon_out} -e {salmon_out} -pe smp {threads}
            """, **self.parse_fq_list(fq_list))

    def join_gene(self):
        self.system("{salmon_path} quantmerge --quants {salmon_out}/*.quant -o {salmon_out}/All.genes.abundance.txt")
        self.clean_header(self.out_dir + "salmon_out/All.genes.abundance.txt", ".quant$")

    def diamond_gene(self, database, out_file, threads=66):
        self.system("""
{diamond_home}/diamond blastp --db {database} --query {assembly_out}/NR.protein.fa --outfmt 6 --threads {threads} \
 -e 0.001 --max-target-seqs 1 --block-size 200 --index-chunks 1 --tmpdir /dev/shm/  --quiet --out {salmon_out}/{out_file}
            """, out_file=out_file, threads=threads, database=database)

    def map_gene(self, threads=70):
        self.system('''
{emapper_path} -m diamond --no_annot --no_file_comments --data_dir {emapper_database} --cpu {threads} \
  -i {assembly_out}/NR.protein.fa -o {salmon_out}/genes --usemem --override

{emapper_path} --annotate_hits_table {salmon_out}/genes.emapper.seed_orthologs --no_file_comments \
  -o {salmon_out}/genes --cpu {threads} --data_dir {emapper_database} --usemem --override
sed -i '1 i Name\teggNOG\tEvalue\tScore\tGeneName\tGO\tKO\tBiGG\tTax\tOG\tBestOG\tCOG\tAnnotation' {salmon_out}/genes.emapper.annotations
            ''', threads=threads)
        self.diamond_gene(self.cazy_database, 'genes_cazy.f6', threads)
        self.diamond_gene(self.fmap_home + '/FMAP_data/protein_fasta_protein_homolog_model_cleaned.dmnd',
                          'genes_card.f6', threads)

    def alloc_src(self, proc, threads=False, sam_num=False):
        memery_needs = self.memery_needs[proc]
        if not sam_num:
            sample_number = self.memery // memery_needs
            sample_number = sample_number if sample_number < self.threads else self.threads
            sample_number = sample_number if sample_number > 1 else 1
        else:
            sample_number = sam_num
        threads = threads if threads else (self.threads // sample_number)
        print("For {}:\nSample number per run is: {}\n Threads number per sample is {}\n Memery size per sample is {}".format(
            proc, sample_number, threads, memery_needs))
        return {
            "sample_number": sample_number,
            "src": {
                "threads": threads,
                "mem": memery_needs
            }
        }

    def find_file(self, directory, pattern):
        for file in os.listdir(directory):
            if re.search(pattern, file):
                return os.path.join(directory, file)
        return None

    def search_fqc(self, fqc_file):
        with open(fqc_file) as f:
            fqc = f.read()
        tree = html.fromstring(fqc)
        num_reads = tree.xpath('//td[text()="Total Sequences"]/following-sibling::td[1]/text()')
        gc_content = tree.xpath('//td[text()="%GC"]/following-sibling::td[1]/text()')
        return int(num_reads[0]), int(gc_content[0])

    def q20_q30(self, read_file):
        qr = list(os.popen("{base_dir}/sim_fqstat {r1}".format(base_dir=self.base_dir, r1=read_file)))
        bases, q20_cnt, q30_cnt = [int(i) for i in qr[0].split()]
        return np.round(q20_cnt / bases * 100, 2), np.round(q30_cnt / bases * 100, 2)

    def get_qc_stats(self, sample_id):
        target_dir = os.path.join(self.kneaddata_out, "fastqc")
        results = OrderedDict([
            ("Sample ID", sample_id),
            ("InsertSize(bp)", "350"),
            ("SeqStrategy", "(150:150)"),
        ])
        raw_fqc = self.find_file(target_dir, "reformatted.*_{}_R1_fastqc.html".format(sample_id))
        raw_num_reads, raw_gc_content = self.search_fqc(raw_fqc)
        clean_fqc = self.find_file(target_dir, "{}_R\d.*paired_1_fastqc.html".format(sample_id))
        clean_num_reads, clean_gc_content = self.search_fqc(clean_fqc)
        raw_q20, raw_q30 = self.q20_q30(self.raw_pattern.format(sample_id=sample_id, direction="R1"))
        clean_q20, clean_q30 = self.q20_q30(self.clean_paired_pattern.format(sample_id=sample_id, direction_num=1))

        results.update([
            ("RawReads(#)", raw_num_reads),
            ("Raw Base(GB)", np.round(raw_num_reads * 300 / 10**9, 2)),
            ("%GC", raw_gc_content),
            ("Raw Q20(%)", raw_q20),
            ("Raw Q30(%)", raw_q30),
            ("Clean Reads(#)", clean_num_reads),
            ("Cleaned(%)", np.round(clean_num_reads / raw_num_reads * 100, 2)),
            ("Clean Q20(%)", clean_q20),
            ("Clean Q30(%)", clean_q30),
        ])
        return results

    def generate_qc_report(self, processors=2):
        executor = ThreadPoolExecutor(max_workers=processors)
        futures = []
        for sample in self.new_ids:
            future = executor.submit(self.get_qc_stats, sample)
            futures.append(future)
        executor.shutdown(True)
        with open(os.path.join(self.report_out, "reads_summary.txt"), 'w') as f:
            for num, future in enumerate(futures):
                stat = future.result()
                if num == 0:
                    f.write('\t'.join(stat.keys()) + '\n')
                vals = [str(v) for v in stat.values()]
                f.write('\t'.join(vals) + '\n')

    def visualize(self):
        VisualizeAll(self.mapping_file, self.categories).visualize(self.exclude, self.base_on_assembly)

    def clean(self):
        self.system("rm -r {tmp_dir}")

    def run(self):
        """
        电脑内存：250G

        电脑逻辑CPU个数：72

        目前:
            kraken2每个样本需要内存：数据库大小（70G）

            Metaphlan2每个样本需要内存：数据库大小（1.5G）

            FMAP每个样本需要内存：数据库大小（uniref90, 2.5G; ARDB, 100M）× threads 个数
        """
        """
        self.format_raw()
        sam_num = int(self.memery * 0.9 / 88)
        sam_num = sam_num if sam_num < 5 else 5
        srcs = self.alloc_src("kneaddata", threads=False, sam_num=sam_num)
        self.run_kneaddata(fq_list=self.paired_data(
            self.raw_pattern, srcs['sample_number']), shift_results=self.kneaddata_out, **srcs['src'])

        self.generate_qc_report()
        """
        srcs = self.alloc_src("kraken2", threads=False)
        self.run_kraken2(fq_list=self.paired_data(self.clean_paired_pattern,
                                                  srcs['sample_number']), **srcs['src'])
        self.run_bracken()

        if self.base_on_assembly:
            self.run_assembly(threads=self.threads)
            self.run_quast()
            self.create_gene_db(threads=self.threads)
            srcs = self.alloc_src("salmon", threads=False)
            self.quant_gene(fq_list=self.paired_data(self.clean_paired_pattern,
                                                     srcs['sample_number']), **srcs['src'], first_check=5)
            self.join_gene()
            self.map_gene(threads=self.threads)
        else:
            srcs = self.alloc_src("humann2", threads=False)
            self.run_humann2(fq_list=self.map_list(self.clean_paired_pattern,
                                                   srcs['sample_number'], use_direction="R1"), **srcs['src'])
            self.join_humann()
            # self.join_metaphlan()
            srcs = self.alloc_src("fmap", threads=False)
            self.fmap_wrapper(fq_list=self.map_list(self.clean_paired_pattern,
                                                    srcs['sample_number'], use_direction="R1"), run_type="AMR", **srcs['src'])
        self.visualize()
        self.clean()
