import argparse

# TODO: fill the descriptions
parser = argparse.ArgumentParser(description='Sprime')
parser.add_argument('-p', '--populations', help='populations to execute in Sprime,default all')
parser.add_argument('-t', '--threads', help='max numbers of threads in allocating processing populations',
                    type=int, default=5)
parser.add_argument('-j', '--process',
                    help='max numbers of processes in allocating processing chromosomes',
                    type=int, default=22)
parser.add_argument('-s', '--sprimethreads',
                    help='max numbers of threads in allocating processing populations in sprime.jar ',
                    type=int, default=2)
parser.add_argument('-m', '--sprimeprocess',
                    help='max numbers of processes in allocating chromosomes in sprime.jar', type=int, default=2)
parser.add_argument('-c', '--config', help='config file path', default="Config.ini", type=str)
args = parser.parse_args()
