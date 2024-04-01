import os, sys
import argparse

def setup_parser():
    parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('files', nargs='*',
                    help='''Input file format can be found in template.inp in /installdir/automable/utils/''')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
    args = parser.parse_args()

    if len(args.files) != 1:
        print("So far the program can handle only one .inp file at once")
        sys.exit()
    else:
        prel_info_obj = []
        with open(args.files[0], "r") as set_file:
            for line in set_file:
                tmp_line = ""
                for char in line:
                    if char == "#":
                        break
                    else:
                        tmp_line += char
                if not (tmp_line == '' or tmp_line == '\n'):
                    prel_info_obj.append(tmp_line)
    # setup needs to go to where inp file is
    # check if only one .inp file and open it 
    # parse data into info object
    # likely should write a block parser function for this
    return prel_info_obj

def xyz_parser():
    return None

def inp_parser():
    return None

def out_parser(catchphrase, block_len):
    return None

print(setup_parser())