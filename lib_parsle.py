import os

def setup_parser():
    curr_dir_cont  = os.listdir(os.getcwd())
    return curr_dir_cont

print(setup_parser())