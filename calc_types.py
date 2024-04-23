#! /usr/bin/python3
import os
from os.path import isfile, isdir

def main():
	freq_from_geom(nprocs='33', maxcore='12000', add='\n%geom\ninhess read\ninhessname "in.hess"\nend\n')
	#print("this is a lib")

def freq_from_geom(**kwargs):
    try:
        os.mkdir("./freq/")
        yesno = 'n'
    except FileExistsError:
        print("Frequency calculation directory exists, do you want to run another freq calc? [y/n]")
        yesno = input("")
        if yesno == 'y':
            print("Calc will be conducted in freq_1")
            os.mkdir("./freq_1")
        if yesno == 'n':
            print("We will stop here.")
            quit()
    cwd = os.getcwd()
    if yesno == 'y':
         newdir = 'freq_1/'
    else:
         newdir = 'freq/'
    prev_inp_file = [f for f in os.listdir(cwd) if isfile(f) and '.inp' in f][0]
    with open(prev_inp_file, 'r') as file:
         prev_inp_str = file.readlines()
    for line in prev_inp_str:
         if 'opt' in line.casefold():
              prev_inp_str[prev_inp_str.index(line)] = '! TightSCF Freq \n'
         for key in kwargs.keys():
              if key.casefold() in line.casefold():
                   prev_inp_str[prev_inp_str.index(line)] = key +' '+ str(kwargs[key]) +'\n'
    with open(newdir+"experimental.inp", 'w') as file:
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