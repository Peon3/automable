# this will write input files etc, should take a class object, I'ld say, there should be a global and a local info object

settings_info = { "functional" : ("bp86", "b3lyp", "tpssh", "pbe0"),
                  "basis" : ("def2-tzvp" , "AutoAux") }

for i in settings_info["functional"]:
    print(i)

#first define all regular info_objects, than define the schedule info_object