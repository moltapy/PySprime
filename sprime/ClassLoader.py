import Functions
from collections import defaultdict


class SampleList:
    def __init__(self, path: str, outgroup: str = None, headerTag: bool = True, popRange=None):
        # TODO:content checker
        self.samplePath = Functions.fileChecker(path)
        self.headerTag, self.outgroupName, self.outgroupList = headerTag, outgroup, None
        self.popRange = popRange
        self.targetPops = self.initTargetPops()

    def initTargetPops(self):
        populationDict = defaultdict(list)
        infile = open(self.samplePath, 'rt')
        header = infile.readline() if self.headerTag else None
        sampleArray, populationArray = Functions.funcSelector(Functions.indexByHeader, Functions.indexByPos, header)
        for line in infile:
            # TODO:兼容性，具体使用的时候要改成\t
            line = line.strip().split()
            populationDict[line[populationArray]].append(line[sampleArray])
        self.outgroupList = populationDict[self.outgroupName]
        populationDict.pop(self.outgroupName)
        if self.popRange:
            # TODO: 统一规范并编写说明
            self.popRange = self.popRange.strip().split(',')
            for popName in self.popRange:
                if not popName in populationDict:
                    print(f"{popName} not in {self.samplePath},Please check!\n")
                    exit(1)
            else:
                populationDict = {popName: populationDict[popName] for popName in self.popRange}

        return populationDict

