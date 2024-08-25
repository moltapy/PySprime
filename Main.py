import os
from tqdm import tqdm

import Functions
# import LogLoader
from ClassLoader import *
from ConfigLoader import *
from concurrent.futures import *
from Parser import args

dirname = f"{os.getcwd()}/Sprime_Out"
populations = args.populations

if __name__ == "__main__":
    os.makedirs(dirname, exist_ok=True)
    sample = SampleList(samplelist, outgroup=outgroup, headerTag=sampleheader, popRange='GBR,FIN')
    outgroup_path = f"{dirname}/{outgroup_name}"
    with open(outgroup_path, "wt") as out:
        for item in sample.outgroupList:
            out.write(f"{item}\n")
    # Extract sample id from samplelist and cluster with outgroup samples
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            futures = [pool.submit(Functions.sampleCluster, dirname, name, item+sample.outgroupList)
                       for name, item in sample.targetPops.items()]
            for future in tqdm(as_completed(futures), total=len(futures), desc="Extract and Cluster"):
                future.result()
    except Exception as error:
        print(f"Error Occurred when processing {Functions.sampleCluster.__name__}", error)
        exit(1)

    # Bcftools split VCF files, get VCF files with a certain modern population and outgroup population
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            futures = [pool.submit(Functions.subExtractor, f"{dirname}/{name}", name, modern_list,
                                   [f"{dirname}/{name}/{item}" for item in submodern_list]) for name in sample.targetPops]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Bcftools Generate VCFfiles"):
                future.result()
    except Exception as error:
        print(f"Error Occurred when processing {Functions.subExtractor.__name__}", error)
        exit(1)

    # Bcftools concat VCF files
    try:
        with Functions.ProcessPoolExecutor(max_workers=args.threads) as pool:
            futures = [pool.submit(Functions.bcfContactor, dirname, name, submodern_list, concated_file)
                       for name in sample.targetPops]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Bcftools Concatenate VCFfiles"):
                future.result()
    except Exception as error:
        print(f"Error Occurred when processing {Functions.bcfContactor.__name__}", error)
        exit(1)
    # Run sprime.jar to get score files
    try:
        with ThreadPoolExecutor(max_workers=args.sprimethreads) as pool:
            futures = [pool.submit(Functions.sprimeMain, dirname, name, sprime_path,
                                   concated_file, outgroup_name, genetic_map, sprime_out) for name in sample.targetPops]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Sprime Main"):
                future.result()
    except Exception as error:
        print(f"Error Occurred when processing {Functions.sprimeMain.__name__}", error)
        exit(1)

    # Mapping Archaic
    try:
        with ThreadPoolExecutor(max_workers=args.threads) as pool:
            futures = [pool.submit(Functions.mappingArchaic, dirname, name, maparch, neandtag, neandmask, neanderthal,
                                   denitag, denimask, denisovan, sprime_out, neandoutfile, denioutfile)
                       for name in sample.targetPops]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"Sprime Mapping"):
                future.result()
    except Exception as error:
        print(f"Error Occurred when processing {Functions.mappingArchaic.__name__}", error)
        exit(1)

    # Summary Matched Score Files and Draw Contour plots
    try:
        with ProcessPoolExecutor(max_workers=args.threads) as pool:
            futures = [pool.submit(Functions.contourDrawer, summary_script, draw_script, dirname, name)
                       for name in sample.targetPops]
            for future in tqdm(as_completed(futures), total=len(futures), desc=f"ContourDrawer"):
                future.result()
    except Exception as error:
        print(f"Error Occurred when processing {Functions.contourDrawer.__name__}", error)
        exit(1)

## 设计思想：html显示最终是一种延迟，也就是最后的图像展示，是请求式生成，先生成一个列表，然后按照需求发送get请求生成
## log和tqdm后续完善
## 优化：两个方向：
# 1. log日志
# 2. 作图写选择式
# 3. 配置提醒
# tqdm进度条，日志？不用重定向，使用日志记录
