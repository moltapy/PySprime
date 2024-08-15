import configparser
import Functions
from ClassLoader import *

config = configparser.ConfigParser()
config.read('config.ini')

# Paths:
## samplelist.txt
samplelist = config['Sample_List_File']['path']
## outgroup
outgroup = config['Outgroup']['pop']
## modern VCF file,using {chrom} to take places
modern = config['Modern_Variants_File']['path']
## modern VCF file,extends {chrom} to a full list
modern_list = [modern.format(chrom=chr) for chr in range(1, 23)]
## generated VCF file path per subgroup
submodern_list = [config['Submodern_Variants_File']['path'].format(chrom=chr) for chr in range(1, 23)]
## path to sprime.jar
sprime_path = config['Sample_List_File']['path']
## genetic map file
genetic_map = config['Genetic_Map_File']['path']
## generated outgroup.txt path
outgroup_path = config['Outgroup_Sample_List']['path']
## VCF file name after concat
concated_file = config['Concated_Submodern_Variants_File']['name']
## Sprime output score files
sprime_out = config['Sprime_Output_File']['path']
## Sample List with Header,True or False
sampleheader = config['Sample_List_Header']['header']

if __name__ == "__main__":
    sample = SampleList(samplelist, outgroup=outgroup, header=sampleheader)
    # 分离群体中的样本，与outgroup合并
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(Functions.samplecluster, name, item+sample.group_content)
                   for name, item in sample.groups.items()]
        for future in futures:
            future.result()

    # 10个线程，20个进程提交给bcftools进行处理，得到vcf文件
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(Functions.subextract, name, modern_list, submodern_list) for name in sample.groups]
        for future in futures:
            future.result()

    # 将群体中的vcf合并称为一个vcf文件
    with Functions.ProcessPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(Functions.bcfconcat, name, submodern_list, concated_file) for name in sample.groups]
        for future in futures:
            future.result()

    # 运行sprime.jar
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(Functions.sprimemain, name, sprime_path,
                               concated_file, outgroup_path, genetic_map, sprime_out) for name in sample.groups]
        for future in futures:
            future.result()


