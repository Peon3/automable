#! /usr/bin/python3
import os
from os.path import isfile, isdir

modes = {'opt' : ['linear'] ,
         'freq' : ['linear'] ,
         'optts' : ['linear'] ,
         'optfreq' : ['linear'] 
        }


def main():
    setup_followup(nprocs='33', maxcore='12000', add='\n%geom\ninhess read\ninhessname "in.hess"\nend\n')
	#print("this is a lib")

def setup_dir(new_calc_type, mode, *args):
    try:
        if mode == 'linear':
            os.mkdir('./'+new_calc_type+'/')
        elif mode == 'branch':
            for dir_name in args:
                os.mkdir('./'+dir_name+'/')
    except FileExistsError:
        return FileExistsError

""" def write_inp(prev_calc_type, new_calc_type, prev_inp_file, **kwargs):
    try:
        with open(prev_inp_file, 'r') as file:
            prev_inp_str = file.readlines()
        for line in prev_inp_str:
            for type in pos_calc_types:
                if type.casefold() in line.casefold():
                    prev_inp_str[prev_inp_str.index(line)] = '! TightSCF '+ new_calc_type + '\n'
    except Exception:
        return Exception """
    

def setup_followup(new_calc_type, **kwargs):
    try:
        cwd = os.getcwd()
        if len(modes[new_calc_type]) == 1:
            setup_dir(new_calc_type, modes[new_calc_type][0])
        elif len(modes[new_calc_type]) == 2:
            setup_dir(new_calc_type, modes[new_calc_type][0], modes[new_calc_type][1])
        for f in [f for f in os.listdir() if isdir(f)]:
            writecwd = cwd+f
            write_inp(writecwd, info_obj)
    except Exception:
        return Exception

def write_inp(writecwd, info_obj):
    write_obj = 
    with open(writecwd, 'w') as file:
        file.writelines(info_obj)

def setup_followup_old(prev_calc_type, new_calc_type, prev_inp_file, **kwargs):
    try:
        if len(modes[new_calc_type]) == 1:
            setup_dir(new_calc_type, modes[new_calc_type][0])
        elif len(modes[new_calc_type]) == 2:
            setup_dir(new_calc_type, modes[new_calc_type][0], modes[new_calc_type][1])
        write_inp(prev_calc_type, new_calc_type, prev_inp_file, kwargs)
    except Exception:
        return Exception
    cwd = os.getcwd()
    prev_inp_file = [f for f in os.listdir(cwd) if isfile(f) and '.inp' in f][0]
    with open(prev_inp_file, 'r') as file:
         prev_inp_str = file.readlines()
    for line in prev_inp_str:
         if 'opt' in line.casefold():
              prev_inp_str[prev_inp_str.index(line)] = '! TightSCF Freq \n'
         for key in kwargs.keys():
              if key.casefold() in line.casefold():
                   prev_inp_str[prev_inp_str.index(line)] = key +' '+ str(kwargs[key]) +'\n'
    with open(newdir+prev_inp_file, 'w') as file:
         for line in prev_inp_str:
              if '!' in line:
                   file.write(line)
              if '!' not in line:
                   if 'add' in kwargs.keys():
                        file.write(kwargs['add'])
                   break
         for line in prev_inp_str:
              if '!' not in line:
                   file.write(line)



if __name__ == "__main__":
	main()