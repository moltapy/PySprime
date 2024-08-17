import configparser
from concurrent.futures import as_completed, ProcessPoolExecutor
from ClassLoader import *

config = configparser.ConfigParser()
config.read('Config.ini')


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
sprime_path = config['Sprime_Jar_Path']['path']
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
## Mapping Tools
maparch = config['Map_Archaic_Path']['path']
## Neanderthal VCF files
neanderthal = config['Neand_Variants_File']['path']
## Denisovan VCF files
denisovan = config['Deni_Variants_File']['path']
## Neanderthal exclude mask
neandmask = config['Neand_Mask_File']['path']
## Denisovan exclude mask
denimask = config['Denisovan_Mask_File']['path']
## Neanderthal tag
neandtag = config['Neanderthal_Tag']['tag']
## Denisovan tag
denitag = config['Denisovan_Tag']['tag']
## Neanderthal match result file, default phase1
neandoutfile = config['Neand_Output_File']['path']
## Denisovan match result file, default final
denioutfile = config['Denisovan_Output_File']['path']
## Script for summary
summary_script = config['Rscript_Phasing_Plot']['path']
## Script for draw contours
draw_script = config['Rscript_Phasing_Contour']['path']

if __name__ == "__main__":
    sample = SampleList(samplelist, outgroup=outgroup, header=sampleheader)
    with open(outgroup_path, "wt") as out:
        for item in sample.group_content:
            out.write(f"{item}\n")
    # 分离群体中的样本，与outgroup合并
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = [pool.submit(Functions.samplecluster, name, item+sample.group_content)
                   for name, item in sample.groups.items()]
        for future in futures:
            future.result()

    # 10个线程，20个进程提交给bcftools进行处理，得到vcf文件
    with ThreadPoolExecutor(max_workers=5) as pool:
        dirname = os.getcwd()
        futures = [pool.submit(Functions.subextract, f"{dirname}/{name}", name, modern_list,
                               [f"{dirname}/{name}/{item}" for item in submodern_list]) for name in sample.groups]
        for future in futures:
            future.result()

    # 将群体中的vcf合并称为一个vcf文件
    with Functions.ProcessPoolExecutor(max_workers=10) as pool:
        dirname = os.getcwd()
        futures = [pool.submit(Functions.bcfconcat, dirname, name, submodern_list, concated_file)
                   for name in sample.groups]
        for future in futures:
            future.result()

    # 运行sprime.jar
    with ThreadPoolExecutor(max_workers=2) as pool:
        dirname = os.getcwd()
        futures = [pool.submit(Functions.sprimemain, dirname, name, sprime_path,
                               concated_file, outgroup_path, genetic_map, sprime_out) for name in sample.groups]
        for future in futures:
            future.result()

    # Mapping Archaic 
    with ThreadPoolExecutor(max_workers=10) as pool:
        dirname = os.getcwd()
        futures = [pool.submit(Functions.maparch, dirname, name, maparch, neandtag, neandmask, neanderthal,
                               denitag, denimask, denisovan, sprime_out, neandoutfile, denioutfile)
                   for name in list(sample.groups.keys())[:2]]
        for future in futures:
            future.result()

    # Summary Matched Score Files and Draw Contour plots
    with ProcessPoolExecutor(max_workers=10) as pool:
        dirname = os.getcwd()
        futures = [pool.submit(Functions.draw_contour, summary_script, draw_script, dirname, name)
                   for name in list(sample.groups.keys())[:2]]
        for future in as_completed(futures):
            future.result()

## 设计思想：html显示最终是一种延迟，也就是最后的图像展示，是请求式生成，先生成一个列表，然后按照需求发送get请求生成
## log和tqdm后续完善
## 到作图之前的基本逻辑完成了，优化：两个方向：
# 1. log日志
# 2. 作图写选择式
# 3. 配置提醒
