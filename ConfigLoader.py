import configparser


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
## generated outgroup.txt name
outgroup_name = config['Outgroup_Sample_List']['name']
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