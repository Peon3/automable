# this will write input files etc, should take a class object, I'ld say, there should be a global and a local info object

""" settings_info = { "functional" : ("bp86", "b3lyp", "tpssh", "pbe0"),
                  "basis" : ("def2-tzvp" , "AutoAux") }

for i in settings_info["functional"]:
    print(i) """

def main():
    a, error = global_info()
    print(error)
    print('this is a lib')

# we need some info objects. either we have classes which means global info 

class global_info:
    try:
        def __init__(self, projects):
            if len(projects) <= 0:
                return self, Exception
    except TypeError:
         return
            


if __name__ == "__main__":
	main()

#first define all regular info_objects, than define the schedule info_object