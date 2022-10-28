import argparse

parser = argparse.ArgumentParser(description='Translate a hanzi file to pinyin')
parser.add_argument('path', type=str, nargs='+')
args = parser.parse_args()

print(args.path)