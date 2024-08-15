import Decorator
import multiprocessing as mp
import os
# 下面这个起个别名叫进程池管理器
from concurrent.futures import ProcessPoolExecutor, as_completed


# Functions


@Decorator.matching
def headerindex(header) -> tuple:
    # 找sample，pop或者super_pop(后面这个要写一个匹配模式)
    print("Mention: Header Mode, Make Sure your data is under header with 'sample' and 'super_pop'")
    # TODO:届时改成\t
    header = header.strip().split()
    header = {header: index for index, header in enumerate(header)}
    return header["sample"], header["super_pop"]


@Decorator.matching
def nullindex() -> tuple:
    # TODO:如果只有两列怎么办
    print("Mention: Non-header Mode,Make Sure your data is under the first and third column")
    return 0, 2


@Decorator.matching
def samplecluster(name: str, sample: list):
    os.makedirs(name, exist_ok=True)
    with open(name + "/" + name + ".txt", "wt") as outfile:
        for item in sample:
            outfile.write(item + "\n")


@Decorator.matching
def bcfexecutor(sample: str, vcffile: str, output: str):
    try:
        os.system(f"bcftools view --samples-file {sample} {vcffile} | bcftools view -c1 -m2 -M2 -v snps "
                  f"| bcftools annotate -x INFO,^FORMAT/GT -Oz > {output}")
        return True
    except Exception as error:
        print("Error occurred while executing bcftools", error)
        exit(1)


@Decorator.matching
def subextract(name: str, vcffile: list, output: list):
    os.chdir(name)
    with ProcessPoolExecutor(max_workers=22) as executor:
        futures = [executor.submit(bcfexecutor, name, infile, outfile) for infile, outfile in zip(vcffile, output)]
        for future in as_completed(futures):
            future.result()


@Decorator.matching
def bcfconcat(name: str, subfiles: list, output: str):
    os.chdir(name)
    os.makedirs("Concat", exist_ok=True)
    os.chdir("Concat")
    expression = "time bcftools concat"
    for file in subfiles:
        expression += f" {file}"
    expression += f" --naive-force --output-type z -o {output}"
    os.system(expression)


@Decorator.matching
def sprimexecutor(expression: str):
    os.system(expression)


@Decorator.matching
def sprimemain(name: str, sprime_path: str, genotype_file: str, outgroup: str, map_file: str, output: str):
    os.makedirs(f"{name}/Result/Phase1", exist_ok=True)
    os.chdir(f"{name}/Result/Phase1")
    output = [output.format(chrom = chr) for chr in range(1, 23)]
    expressions = [(f"time java -jar {sprime_path} gt={genotype_file} "
                    f"outgroup = {outgroup} map = {map_file} out = {out} chrom = {chrom} minscore=150000")
                   for out,chrom in zip(output, range(1, 23))]
    with ProcessPoolExecutor(max_workers=22) as executor:
        futures = [executor.submit(sprimexecutor, expression) for expression in expressions]
        for future in as_completed(futures):
            future.result()


