#! usr/bin/python3
import argparse
import os, sys


def read_inp() -> list:
    parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('files', nargs='*',
                        help='''Input file format can be found in you mom''')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
    args = parser.parse_args()

    if len(args.files) != 1:
        print("So far the program can handle just one file at a time")
        sys.exit()
    else:
        info_obj = []
        with open(args.files[0], 'r') as set_file:
            info_obj = set_file.readlines()
        for line in info_obj:
            for entry in line.split():
                if entry.casefold() in
    return info_obj

def read_out() -> list:
    parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('files', nargs='*',
                        help='''Input file format can be found in you mom''')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
    args = parser.parse_args()

    if len(args.files) != 1:
        print("So far the program can handle just one file at a time")
        sys.exit()
    else:
        info_obj = []
        with open(args.files[0], 'r') as set_file:
            
    return info_obj

def set_up_geom():
