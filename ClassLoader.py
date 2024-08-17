import os
import Functions
from collections import defaultdict


class SampleList:
    def __init__(self, path: str, outgroup: str = None, header=True):
        # TODO:content checker
        self.path = self.checker(path)
        self.header = header
        self.outgroup = outgroup
        self.group_content = None
        self.groups = self.initpops()

    # 初始化就使用消息队列将模式处理好
    def initpops(self):
        groups = defaultdict(list)
        infile = open(self.path, 'rt')
        header = infile.readline() if self.header else None
        i_sample, i_pop = Functions.selector(Functions.headerindex,
                                             Functions.nullindex, header)
        # O(n),能不能降
        for line in infile:
            # TODO:兼容性，具体使用的时候要改成\t
            line = line.strip().split()
            groups[line[i_pop]].append(line[i_sample])
        self.group_content = groups[self.outgroup]
        groups.pop(self.outgroup)
        return groups

    @staticmethod
    def checker(path: str):
        if os.path.isfile(path):
            return path
        else:
            print("{path} not exists, Please check the path")
            exit(1)
