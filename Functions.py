import os
from tqdm import tqdm
from concurrent.futures import ProcessPoolExecutor, as_completed
from Main import args


# Functions
def fileChecker(path: str):
    if os.path.isfile(path):
        return path
    else:
        print(f"{path} is not a file\n")
        exit(1)


def funcSelector(func1, func2, condition) -> tuple:
    return func1(condition) if condition else func2()


def indexByHeader(header) -> tuple:
    # 找sample，pop或者pop(后面这个要写一个匹配模式)
    # TODO: 优化这里的显示匹配，考虑输出函数名和内容
    print("Mention: Header Mode, Make Sure your data is under header with 'sample' and 'super_pop'")
    # TODO:届时改成\t
    header = header.strip().split()
    header = {header: index for index, header in enumerate(header)}
    return header["sample"], header["pop"]


def indexByPos() -> tuple:
    # TODO:如果只有两列怎么办
    print("Mention: Non-header Mode,Make Sure your data is under the first and third column")
    # 不是super_pop
    # TODO：这个考虑一下处理
    return 0, 1


def sampleCluster(workPath: str, popName: str, sampleList: list):
    dirpath = f"{workPath}/{popName}"
    os.makedirs(dirpath, exist_ok=True)
    with open(dirpath + "/" + popName + ".txt", "wt") as outfile:
        for item in sampleList:
            outfile.write(item + "\n")


def bcfExecutor(popName: str, vcfFilePath: str, output: str):
    print(f"bcfexecutor start ,output={output}")
    try:
        os.system(f"bcftools view --samples-file {popName} {vcfFilePath} | bcftools view -c1 -m2 -M2 -v snps "
                  f"| bcftools annotate -x INFO,^FORMAT/GT -Oz > {output}")
        return True
    except Exception as error:
        print("Error occurred while executing bcftools", error)
        exit(1)


def subExtractor(workPath: str, popName: str, vcfFileLists: list, subVcfFileLists: list):
    sampleFile = f"{workPath}/{popName}.txt"
    print(f"finding {sampleFile} in {os.getcwd()}")
    with ProcessPoolExecutor(max_workers=args.process) as executor:
        futures = [executor.submit(bcfExecutor, sampleFile, inFile, outFile)
                   for inFile, outFile in zip(vcfFileLists, subVcfFileLists)]
        for future in as_completed(futures):
            future.result()
    

def bcfContactor(workPath: str, popName: str, subVcfFileLists: list, concatedVcfFiles: str):
    concatPath = f"{workPath}/{popName}/Concat"
    os.makedirs(concatPath, exist_ok=True)
    expression = "time bcftools concat"
    for fileName in subVcfFileLists:
        expression += f" {workPath}/{popName}/{fileName}"
    expression += f" --naive-force --output-type z -o {concatPath}/{concatedVcfFiles}"
    os.system(expression)


def sprimeExecutor(expression: str):
    os.system(expression)


def sprimeMain(workPath: str, popName: str, sprimePath: str, concatedVcfFile: str,
               outgroupName: str, mapFilePath: str, scoreFilePath: str):
    dirpath = f"{workPath}/{popName}/Result/Phase1"
    outgroupName = f"{workPath}/{outgroupName}"
    concatedVcfFile = f"{workPath}/{popName}/Concat/{concatedVcfFile}"
    os.makedirs(dirpath, exist_ok=True)
    scoreFilePath = [f"{dirpath}/{scoreFilePath.format(chrom=chr)}" for chr in range(1, 23)]
    expressions = [(f"time java -jar {sprimePath} gt={concatedVcfFile} "
                    f"outgroup={outgroupName} map={mapFilePath} out={out} chrom={chrom} minscore=150000")
                   for out, chrom in zip(scoreFilePath, range(1, 23))]
    with ProcessPoolExecutor(max_workers=args.sprimeprocess) as executor:
        futures = [executor.submit(sprimeExecutor, expression) for expression in expressions]
        for future in as_completed(futures):
            future.result()


def mappingExecutor(expression: tuple):
    os.system(expression[0])
    os.system(expression[1])
    print("mapping over")


def mappingArchaic(workPath: str, popName: str, maparchExecutor: str, tag_x: str, maskfile_x, variant_x,
                   tag_y: str, maskfile_y, variant_y, scorefile, outfile_phase1, outfile_phase2):
    scorefile = f"{workPath}/{popName}/Result/Phase1/{scorefile}"
    dirout_phase1 = f"{workPath}/{popName}/Result/Phase2/"
    dirout_phase2 = f"{workPath}/{popName}/Result/Final/"
    os.makedirs(dirout_phase1, exist_ok=True)
    os.makedirs(dirout_phase2, exist_ok=True)
    outfile_phase1 = f"{workPath}/{popName}/Result/Phase2/{outfile_phase1}"
    outfile_phase2 = f"{workPath}/{popName}/Result/Final/{outfile_phase2}"
    expression = (f"{maparchExecutor} --kp --sep '\t' --tag {tag_x} --mskbed {maskfile_x} --vcf {variant_x}"
                  f" --score {scorefile}.score > {outfile_phase1}", f"{maparchExecutor} --kp --sep '\t' --tag {tag_y} "
                  f"--mskbed {maskfile_y} --vcf {variant_y} --score {outfile_phase1} > {outfile_phase2}")
    expressions = [(expression[0].format(chrom=chr), expression[1].format(chrom=chr)) for chr in range(1, 23)]
    with ProcessPoolExecutor(max_workers=args.process) as executor:
        futures = [executor.submit(mappingExecutor, expression) for expression in expressions]
        for future in as_completed(futures):
            future.result()


def scoreSummary(scriptPath: str, summaryDirPath: str, output: str):
    expression = f"Rscript {scriptPath} {summaryDirPath} {output}"
    os.system(expression)


def contourDrawer(summaryPath: str, contourPath: str, dirname: str, popName: str):
    targetPath = f"{dirname}/{popName}/Result/Final"
    resultPath = f"{targetPath}/Summary/"
    os.makedirs(resultPath, exist_ok=True)
    summary_file = f"{resultPath}/summary.txt"
    expression = f"Rscript {summaryPath} {targetPath} {summary_file}"
    os.system(expression)
    resultPath = f"{resultPath}/{popName}"
    scoreSummary(contourPath, summary_file, resultPath)
