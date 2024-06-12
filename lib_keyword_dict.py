#! usr/bin/python3

def create_keyword_dict() -> dict:
    #########################################################
    #   Returns a dict with (nearly) all orca keywords      #
    #########################################################

    all_keywords = {
        #####################################################
        # Start basis sets                                  #
        #####################################################
        'def2-svp' : 'basis' ,
        'def2-sv(p)' : 'basis' ,
        'def2-tzvp' : 'basis' ,
        'def2-tzvp(-f)' : 'basis' ,
        'def2-tzvpp' : 'basis' ,
        'def2-qzvp' : 'basis' ,
        'def2-qzvpp' : 'basis' ,
        'def2-5zvp' : 'basis' ,
        'dkh-def2-svp' : 'basis' ,
        'dkh-def2-sv(p)' : 'basis' ,
        'dkh-def2-tzvp' : 'basis' ,
        'dkh-def2-tzvp(-f)' : 'basis' ,
        'dkh-def2-tzvpp' : 'basis' ,
        'dkh-def2-qzvpp' : 'basis' ,
        'zora-def2-svp' : 'basis' ,
        'zora-def2-sv(p)' : 'basis' ,
        'zora-def2-tzvp' : 'basis' ,
        'zora-def2-tzvp(-f)' : 'basis' ,
        'zora-def2-tzvpp' : 'basis' ,
        'zora-def2-qzvpp' : 'basis' ,
        'sarc-zora-tzvp' : 'basis' ,
        'sarc-zora-tzvpp' : 'basis' ,
        'sarc-dkh-tzvp' : 'basis' ,
        'sarc-dkh-tzvpp' : 'basis' ,
        'cc-pvdz' : 'basis' ,
        'cc-pvtz' : 'basis' ,
        'cc-pvqz' : 'basis' ,
        'cc-pv5z' : 'basis' ,
        'aug-cc-pvdz' : 'basis' ,
        'aug-cc-pvtz' : 'basis' ,
        'aug-cc-pvqz' : 'basis' ,
        'aug-cc-pv5z' : 'basis' ,
        'ano-pvdz' : 'basis' ,
        'ano-pvtz' : 'basis' ,
        'ano-pvqz' : 'basis' ,
        'ano-pv5z' : 'basis' ,
        'ano-rcc-dzp' : 'basis' ,
        'ano-rcc-tzp' : 'basis' ,
        'ano-rcc-qzp' : 'basis' ,
        'ano-rcc-full' : 'basis' ,
        'saug-ano-pvdz' : 'basis' ,
        'saug-ano-pvtz' : 'basis' ,
        'saug-ano-pvqz' : 'basis' ,
        'saug-ano-pv5z' : 'basis' ,
        'aug-ano-pvdz' : 'basis' ,
        'aug-ano-pvtz' : 'basis' ,
        'aug-ano-pvqz' : 'basis' ,
        'aug-ano-pv5z' : 'basis' ,
        #####################################################
        # Start Aux basis sets                              #
        #####################################################
        'def2/j' : 'AuxBasisJ' ,
        'sarc/j' : 'AuxBasisJ' ,
        'x2c/j' : 'AuxBasisJ' ,
        'def2/jk' : 'AuxBasisJK' ,
        'def2/jksmall' : 'AuxBasisJK' ,
        'cc-pvdz/jk' : 'AuxBasisJK' ,
        'cc-pvtz/jk' : 'AuxBasisJK' ,
        'cc-pvqz/jk' : 'AuxBasisJK' ,
        'cc-pv5z/jk' : 'AuxBasisJK' ,
        'aug-cc-pvdz/jk' : 'AuxBasisJK' ,
        'aug-cc-pvtz/jk' : 'AuxBasisJK' ,
        'aug-cc-pvqz/jk' : 'AuxBasisJK' ,
        'aug-cc-pv5z/jk' : 'AuxBasisJK' ,
        'def2-svp/c' : 'AuxBasisC' ,
        'def2-tzvp/c' : 'AuxBasisC' ,
        'def2-tzvpp/c' : 'AuxBasisC' ,
        'def2-qzvpp/c' : 'AuxBasisC' ,
        'def2-svpd/c' : 'AuxBasisC' ,
        'def2-tzvpd/c' : 'AuxBasisC' ,
        'def2-tzvppd/c' : 'AuxBasisC' ,
        'def2-qzvppd/c' : 'AuxBasisC' ,
        'cc-pvdz/c' : 'AuxBasisC' ,
        'cc-pvtz/c' : 'AuxBasisC' ,
        'cc-pvqz/c' : 'AuxBasisC' ,
        'cc-pv5z/c' : 'AuxBasisC' ,
        'aug-cc-pvdz/c' : 'AuxBasisC' ,
        'aug-cc-pvtz/c' : 'AuxBasisC' ,
        'aug-cc-pvqz/c' : 'AuxBasisC' ,
        'aug-cc-pv5z/c' : 'AuxBasisC' ,
        'AutoAux' : 'AuxBasisAll' ,
        #####################################################
        # Start CalcTypes and Settings                      #
        #####################################################
        'Opt' : 'CalcType' ,
        'TightOpt' : 'CalcType' ,
        'VeryTightOpt' : 'CalcType' ,
        'Freq' : 'CalcType' ,
        'TightSCF' : 'CalcType' ,
        'VeryTightSCF' : 'CalcType' ,
        'SlowConv' : 'General_CalcSettings' ,
        'VerySlowConv' : 'General_CalcSettings' ,
        'NoTRAH' : 'General_CalcSettings' ,
        'NoDIIS' : 'General_CalcSettings' ,
        'KDIIS' : 'General_CalcSettings' ,
        'SOSCF' : 'General_CalcSettings' ,
        'UKS' : 'General_CalcSettings' ,
        #####################################################
        # Start DFT Functionals                             #
        #####################################################
        'BP' : 'Functional' ,
        'BP86' : 'Functional' ,
        'PBE' : 'Functional' ,
        'B3LYP' : 'Functional' ,
        'BHLYP' : 'Functional' ,
        'TPSS' : 'Functional' ,
        'TPSSh' : 'Functional' ,
        'TPSS0' : 'Functional' ,
        'scanfunc' : 'Functional' ,
        'wB97X-D3' : 'Functional' ,
        'wB97X-D4' : 'Functional' ,
        'wB97X-V' : 'Functional' ,
        'wB97X-D3BJ' : 'Functional' ,
        'wB97M-V' : 'Functional' ,
        'wB97M-D3BJ' : 'Functional' ,
        'wB97M-D4' : 'Functional' ,
        'CAM-B3LYP' : 'Functional' ,
    }
    return all_keywords

def main():
    all_keywords = create_keyword_dict()
    print('dkh-def2-svp'.casefold() in all_keywords)

if __name__ == "__main__":
	main()