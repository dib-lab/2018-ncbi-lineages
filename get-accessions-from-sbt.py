#! /usr/bin/env python
from __future__ import print_function
import sys
import argparse
import csv
import sourmash_lib


def main():
    p = argparse.ArgumentParser()
    p.add_argument('sbt')
    p.add_argument('-o', '--output', type=argparse.FileType('wt'))
    args = p.parse_args()

    db = sourmash_lib.load_sbt_index(args.sbt)

    for n, leaf in enumerate(db.leaves()):
        if n % 1000 == 0:
            print('... at leaf', n)

        name = leaf.data.name()

        # & output!
        args.output.write('{}\n'.format(name))

    print('got accessions from {} signatures'.format(n + 1))


if __name__ == '__main__':
    main()
