#! usr/bin/python3
import argparse
import os, sys
from lib_keyword_dict import create_keyword_dict, create_keyblock_dict

class input_info_objects:
    def __init__(self, name:str):
        setattr(self, 'CalcName', name)

    def sanity_check(self, keyword_dict:dict, keyblock_dict:dict):
        try:
            if (getattr(self, 'basis') in keyword_dict.keys()) == False:
                print('The given basis is not in the list of known basis sets, something wrong here')
                sys.exit()
        except AttributeError:
            print('Your calculation settings are missing a basis set. No matter what you do, that kinda can\'t be right...')


def read_write_inp() -> list:
    parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('file', nargs='1',
                        help='''standard orca inp''')
    parser.add_argument('new_basis', nargs='1',
                        help='''some basis in \'basis\' please ''')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
    args = parser.parse_args()

    if len(args.file) != 1:
        print("So far the program can handle just one file at a time")
        sys.exit()
    else:
        new_lines = []
        keyword_dict = create_keyword_dict
        with open(args.file[0], 'r') as set_file:
            all_lines = set_file.readlines()
        for line in all_lines:
            for entry in line.split():
                if entry.casefold() in keyword_dict and keyword_dict[entry.casefold()] == 'basis'.casefold() and '!' in line.casefold():
                    new_lines.add('! '+args.new_basis) 
                elif entry.casefold() in keyword_dict and '!' in line.casefold():
                    print('kekw')
    return info_obj

""" def read_inp_help() -> list:    # tis for later to adapt, for now we go for a simple approach
    parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('files', nargs='*',
                        help='''Input file format can be found in you mom''')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
    args = parser.parse_args()

    if len(args.files) != 1:
        print("So far the program can handle just one file at a time")
        sys.exit()
    else:
        info_obj = dict()
        keyword_dict = create_keyword_dict
        with open(args.files[0], 'r') as set_file:
            all_lines = set_file.readlines()
        for line in all_lines:
            for entry in line.split():
                if entry.casefold() in keyword_dict and keyword_dict[entry.casefold()] == 'basis'.casefold():
                    info_obj['basis'] = 
    return info_obj """

""" def read_out() -> list:
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

    """
