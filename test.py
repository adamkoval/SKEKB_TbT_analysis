import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--test',
                    nargs='?',
                    const='2')
args = parser.parse_args()

if args.test is not None:
    print(args.test)
