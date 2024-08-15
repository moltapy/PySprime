from Functions import *


genotype_file = "123/456/78{chrom}.vcf"

genotype_file= genotype_file.format(chrom="chr12")

print(genotype_file)