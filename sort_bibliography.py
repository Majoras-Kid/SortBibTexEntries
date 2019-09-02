import re
import os


home = "/home/florian/"

# RegExp Pattern
input_pattern = "\\input\{(.)*.tex\}"
cite_pattern = "\\cite\{[a-zA-Z0-9, ]*\}"
bibtex_pattern = "\\bibliography\{[a-zA-Z0-9/_.]*\}"

source_pattern = "@([a-zA-Z]+{)"

# Bibtex file that will be sorted
bibtex_file = "NOT_FOUND"
bib_dict = dict()


cite_list = list()

def get_bibtex_entry():
    global bibtex_file
    global bib_dict

    if bibtex_file == "NOT_FOUND":
        print("\t[!] No bibtex file was found!")
        return
    
    bib = open(bibtex_file,"r")
    line = bib.readline()
    while(line):
        #print("Line: '%s'" % line)

        begin = re.match(source_pattern,line)
        
        #start of source definition
        if begin:
            print("")
            #get identifier
            ident = line.replace(begin.group(0),"")
            ident = ident.replace(",\n","")
            print("\t[+] Found ident: '%s'" % ident) 
            source =line
            source_line = bib.readline()
            
            #read current source definition
            while(source_line[-2:] != "}\n"):
                source += source_line
                source_line = bib.readline()

            source +=source_line

            braket_open = source.count('{')
            braket_close = source.count('}')

            if(braket_open > braket_close):
                #print("\t[!] Warning, braket count wrong: %s (%i:%i)! Adding one" % (ident,braket_open, braket_close))
                source += "}\n"
            source += "\n"

            # store identifier and source in dictionary
            #print("\t[+] Adding source to dictionary")
            bib_dict.update( {ident : source })
            source = ""
            ident = ""
            print("\t[+] Done reading current source!")
            
            

        line = bib.readline()
 #   print("\t[+] Keys: ", bib_dict.keys())


def get_bib_tex_file(main_tex):
    global bibtex_file
    global bibtex_pattern
    bibtex = open(main_tex,"r")
    for line in bibtex:
        if "\\bibliography{" in line:
            bibtex_file = line.replace(" ", "")
            bibtex_file = bibtex_file.replace("\\bibliography{", "")
            bibtex_file = bibtex_file.replace("}", "")
            bibtex_file = bibtex_file.replace("\n","")
            print("\t[+] Bibtex_file: %s" % bibtex_file)
            bibtex.close()
            return

        #this regexp simply does not want to work
        #TODO
        file = re.match("\\bibliography\{(.*?)\}", line)
        
        if file:
            print("\t[+] FINALY FOUND WITH REGEX")
            file = file.group(1).split(",")
            file = file.replace("\\bibliography{","")
            file = file.replace("}","")
            print("\t[+] Found bibtex file: '%s'",file)
            return

    print("\t[-] No bibtex file found!")
    bibtex.close()

def read_tex_file(tex_file):
    global cite_pattern
    global input_pattern
    global main_tex_folder
    global cite_list

    file = open(tex_file,"r")

    for i,line in enumerate(file):
        #print("[-] Testing: (%i): %s" % (i, line.replace("\n","")))
        input_match = re.search(input_pattern,line)
        cite_match = re.search(cite_pattern, line)
        if input_match:
            new_file = (re.search("\{(.)*\}",line)).group(0)[1:-1]
            new_file = "%s%s" % (main_tex_folder,new_file)
            print("\t[+] Input request found, adding file ")
            read_tex_file(new_file)
            

        if cite_match:
            cites = re.findall(cite_pattern,line)

            for cite in cites:
                cite = (((cite.replace("cite{","")).replace("}","")).replace(" ","")).split(",")
                #print("\t[-] Testing cite: ", cite)
                for c in cite: 
                    if(c not in cite_list):
                        #print("\t[+] Adding cite: ", c)
                        cite_list.append(c)


def create_new_bibtex():
    global bib_dict
    global cite_list
    global bibtex_file

    new_file_name = "%s_temp.bib" % bibtex_file[:-4]
    file = open(new_file_name, "w+")
    print("\t[+] Creating new bibtext file: '%s'" % new_file_name)
    
    for i,c in enumerate(cite_list):
        #print("\t[+] Adding entry %s at \t\t%i" % (c,i))
        #print("\t", bib_dict.get(c), "\n")
        if(bib_dict.get(c) != None):
            file.write(bib_dict.get(c))
    
    file.close()

main_tex_folder = ("%sDocuments/hiwi/funkeybox/00_documentation/2019-xx_FunkeyBox_Paper/Text/" % home)
os.chdir(main_tex_folder)

print("[+] Starting to look for bibtex file")
get_bib_tex_file("box.tex")
get_bibtex_entry()
print("[+] Starting to gather cites!")
read_tex_file("box.tex")

print("\n[+] Sorted %i entries from cites from documents: \n" %(len(cite_list)))

print("[+] Creating new bibtex file")
create_new_bibtex()

