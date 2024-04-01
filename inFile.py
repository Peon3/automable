def inFile():
    # handles input files and detects running mode, also does the setup by calling load and setup functions
    LVerbMode = 0
    parser = argparse.ArgumentParser(add_help=False, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('files', nargs='*',
                    help='''Input file format:\nfile reaction_rate_constants.csv\nparticles particle#\nstates state1 state2 ...\npercentage state1%% state2%% ...\nsteps stepnumber''')
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS, help='Show this help message and exit.')
    parser.add_argument('-v', '--verbose', help='''0 = only necessary out + a little magic\n1 = make the program talk to you like a fortnite kid\ndefault = 0''')
    args = parser.parse_args()
    if args.verbose != None:
        LVerbMode = int(args.verbose)
    if len(args.files) == 0:
        LPMatrix, LPopSVec, LstepNr, LcountNr, LGErrorCode = totalSetup()
        return LPMatrix, LPopSVec, LstepNr, LcountNr, LGErrorCode, LVerbMode
    elif len(args.files) == 1:
        for line in open(args.files[0]):
            if 'file' in line.lower():
                FName = line.split(' ')[-1][:-1]
            elif 'particles' in line.lower():
                LcountNr = line.split(' ')[-1][:-1]
            elif 'states' in line.lower():
                pop_states = line.split(' ')[1:-1]
                pop_states.append(line.split(' ')[-1][:-1])
                if '' in pop_states:
                    pop_states.remove('')
            elif 'percentage' in line.lower():
                proC_states = line.split(' ')[1:-1]
                proC_states.append(line.split(' ')[-1][:-1])
                if '' in proC_states:
                    proC_states.remove('')
            elif 'steps' in line.lower():
                n_steps = line.split(' ')[-1][:-1]
            else:
                print("Something went wrong in your infile.")
        LPMatrix, LGErrorCode = csvParser(FName)
        errorTerminate(LGErrorCode)
        LPopSVec, LGErrorCode = setup(LPMatrix)
        errorTerminate(LGErrorCode)
        LPopSVec, LstepNr, LcountNr, LGErrorCode = fineSetup(LPopSVec, LcountNr, pop_states, proC_states, n_steps)
        errorTerminate(LGErrorCode)
        return LPMatrix, LPopSVec, LstepNr, LcountNr, LGErrorCode, LVerbMode
    elif len(args.files) >= 1:
        print("Program can handle only one infile.\nProgram will stop executing here.")
        sys.exit()
