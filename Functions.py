import Decorator
import os
import time
# 下面这个起个别名叫进程池管理器
from concurrent.futures import ProcessPoolExecutor, as_completed


# Functions


@Decorator.matching
def headerindex(header) -> tuple:
    # 找sample，pop或者pop(后面这个要写一个匹配模式)
    print("Mention: Header Mode, Make Sure your data is under header with 'sample' and 'super_pop'")
    # TODO:届时改成\t
    header = header.strip().split()
    header = {header: index for index, header in enumerate(header)}
    return header["sample"], header["pop"]


@Decorator.matching
def nullindex() -> tuple:
    # TODO:如果只有两列怎么办
    print("Mention: Non-header Mode,Make Sure your data is under the first and third column")
    # 不是super_pop
    return 0, 1


@Decorator.matching
def samplecluster(name: str, sample: list):
    os.makedirs(name, exist_ok=True)
    with open(name + "/" + name + ".txt", "wt") as outfile:
        for item in sample:
            outfile.write(item + "\n")


def bcfexecutor(sample: str, vcffile: str, output: str):
    print(f"bcfexecutor start ,output={output}")
    try:
        print(f"finding {sample} in {os.getcwd()}")
        os.system(f"bcftools view --samples-file {sample} {vcffile} | bcftools view -c1 -m2 -M2 -v snps "
                  f"| bcftools annotate -x INFO,^FORMAT/GT -Oz > {output}")
        print("bcfends")
        return True
    except Exception as error:
        print("Error occurred while executing bcftools", error)
        exit(1)


def subextract(path: str, name: str, infile: list, outfile: list):
    samplefile = f"{path}/{name}.txt"
    print(f"finding {samplefile} in {os.getcwd()}")
    with ProcessPoolExecutor(max_workers=22) as executor:
        futures = [executor.submit(bcfexecutor, samplefile, filein, fileout)
                   for filein, fileout in zip(infile, outfile)]
        for future in as_completed(futures):
            future.result()
    

def bcfconcat(path: str, name: str, subfiles: list, output: str):
    concat_path = f"{path}/{name}/Concat"
    os.makedirs(concat_path, exist_ok=True)
    expression = "time bcftools concat"
    for file in subfiles:
        expression += f" {path}/{name}/{file}"
    expression += f" --naive-force --output-type z -o {concat_path}/{output}"
    os.system(expression)


def sprimexecutor(expression: str):
    os.system(expression)


@Decorator.matching
def sprimemain(path: str, name: str, sprime_path: str, genotype_file: str, outgroup: str, map_file: str, output: str):
    dirpath = f"{path}/{name}/Result/Phase1"
    genotype_file = f"{path}/{name}/Concat/{genotype_file}"
    os.makedirs(dirpath, exist_ok=True)
    output = [f"{dirpath}/{output.format(chrom=chr)}" for chr in range(1, 23)]
    expressions = [(f"time java -jar {sprime_path} gt={genotype_file} "
                    f"outgroup={outgroup} map={map_file} out={out} chrom={chrom} minscore=150000")
                   for out, chrom in zip(output, range(1, 23))]
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(sprimexecutor, expression) for expression in expressions]
        for future in as_completed(futures):
            future.result()


def mapexecutor(expression:tuple):
    os.system(expression[0])
    os.system(expression[1])
    print("mapping over")


def maparch(path: str, pop: str, executable: str, tag_x: str, maskfile_x, variant_x,
            tag_y: str, maskfile_y, variant_y, scorefile, outfile_phase1, outfile_phase2):
    scorefile = f"{path}/{pop}/Result/Phase1/{scorefile}"
    outfile_phase1 = f"{path}/{pop}/Result/Phase2/{outfile_phase1}"
    outfile_phase2 = f"{path}/{pop}/Result/Final/{outfile_phase2}"
    expression = (f"{executable} --kp --sep '\t' --tag {tag_x} --mskbed {maskfile_x} --vcf {variant_x}"
                  f"--score {scorefile} > {outfile_phase1}", f"{executable} --kp --sep '\t' --tag {tag_y} "
                  f"--mskbed {maskfile_y} --vcf {variant_y} --score {outfile_phase1} > {outfile_phase2}")
    expressions = [(expression[0].format(chrom=chr), expression[1].format(chrom=chr)) for chr in range(1, 23)]
    with ProcessPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(mapexecutor, expression) for expression in expressions]
        for future in as_completed(futures):
            future.result()
