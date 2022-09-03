#!/usr/bin/python

#####################################################################
### PubchemPropertiesFromCompoundNames.py  08/30/22 - Sam Bassett ###
#####################################################################

'''
Arguments for running in command line [1]: input file name, [2]: output file name

This script automates retrieval of molecular formulas, monoisotpic mass, isomeric 
SMILES codes, and CIDs from Pubchem given a list of compound names in the form of a CSV.
The header of the first column should be "compoundName" and the csv must be saved
in your working directory as a CSV UTF-8 filetype (this is an option in the save as
dropdown menu in excel). When opening in excel, select semicolons as the delimiter.

Can be further adapted to retrieve any property from pubchem in accoradance
with PUG-Rest documentation: https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest

Code adapted from Angelika Keller: https://kellerbits.net/wordpress/?p=326
'''

# Import the library necessary for making a web service request.
import sys
import urllib.request
import urllib.error
import json
import time
import pandas as pd
import re

# Read in your .csv list with names where info is to be requested, format your output csv, write out your collected info
def main(inputFile, outputFile):
    df = pd.read_csv(input_file_name, sep = ';', encoding = 'utf-8')
    list_name = df['compoundName'].astype(str).values.tolist()
    
    organize = 'Compound Name;Molecular Formula;Monoisotopic Mass;SMILES;CID\n'
    output = map_name_list_to_csv(list_name) # call function for generating final result
    final = organize + output # now final contains a complete csv as string, just write it out to a file.

    with open(output_file_name, "w", encoding = 'utf-8-sig' ) as file:
        file.write(final)
    
# Specify input file name
input_file_name = sys.argv[1]

# Specify desired output file name
output_file_name = sys.argv[2]

# Function to map all your collected info to your csv file
def map_name_list_to_csv(list_name):
    output = ''
    for name in list_name:
        if len(str(name)) > 0:
            name = greekSymbolToWord(name)
            molecularFormula = compoundName_to_Property(name, "PropertyTable", "MolecularFormula")
            if molecularFormula != "Failed": #Speeds up the process a bit, if your formula fails all other properties will inevitably fail too and we can skip searching for them
                monoisotopicMass = compoundName_to_Property(name, "PropertyTable", "MonoisotopicMass")
                time.sleep(0.5) # Don't want to overload pubchem with requests
                smiles = compoundName_to_Property(name, "PropertyTable", "IsomericSMILES")
                time.sleep(0.5)
                CID = str(compoundName_to_Property(name, "IdentifierList", "cids"))
                time.sleep(0.5)
            else:
                smiles = "Failed"
                monoisotopicMass = "Failed"
                CID = "Failed"
                
            if len(molecularFormula) > 0:
                name = greekWordToSymbol(name)
                line = name + ';' + molecularFormula + ';' + monoisotopicMass + ';' + smiles + ';' + CID
                output = output + line + '\n' # create and concatenate output
                print('\n', line)

    return output

# Functions for dealing with greek letters
def greekSymbolToWord(name):
    if len(str(name)) > 0:
        name = re.sub('α', "alpha", name) #Must replace utf-8 greek letters with their written names for pubchem to search them
        name = re.sub('β', "beta", name)
        name = re.sub('γ', "gamma", name)
        name = re.sub('δ', "sigma", name)
        name = re.sub('λ', "lambda", name)
        name = re.sub(' ', '-', name)
        return name

def greekWordToSymbol(name):
    if len(str(name)) > 0:
        name = re.sub("alpha", 'α' , name) #Reverting back to the original greek letters for output in csv
        name = re.sub("beta", 'β', name)
        name = re.sub("gamma", 'γ', name)
        name = re.sub("sigma", 'δ', name)
        name = re.sub("lambda", 'λ', name)
        name = re.sub('-', ' ', name)
        return name

# Function for querying Pubchem and storing results to output
def compoundName_to_Property(compoundName, tableType, Property):
    if Property != "cids":
        path_prolog = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
        path_compound = '/compound/'
        path_name = 'name/'
        path_compoundName = str(compoundName)
        path_Property = '/property/' + Property
        path_JSON = '/JSON'
        
        url = path_prolog + path_compound + path_name + path_compoundName + path_Property + path_JSON
        
        # Make a PUG-REST request and store the output in "request". CID requests have a different format so they get their own loop.  
        try:
            request = urllib.request.urlopen(url)
        except urllib.error.HTTPError:
            Property = "Failed"
            return Property
            
        # Give the reply in JSON format, access and store your property
        if request is not None:
            reply = request.read()
            if reply is not None and len(reply) > 0:
                json_out = json.loads(reply)
                #return json_out
                Property = json_out[tableType]['Properties'][0][Property]
                return Property
            return ''
        
    if Property == "cids":
        path_prolog = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug'
        path_compound = '/compound/'
        path_name = 'name/'
        path_compoundName = str(compoundName)
        path_Property = '/'+  Property
        path_JSON = '/JSON'
        
        url = path_prolog + path_compound + path_name + path_compoundName + path_Property + path_JSON
        
        try:
            request = urllib.request.urlopen(url)
        except urllib.error.HTTPError:
            Property = "Failed"
            return Property
        
        if request is not None:
            reply = request.read()
            if reply is not None and len(reply) > 0:
                json_out = json.loads(reply)
                #return json_out
                Property = json_out[tableType]['CID'][0]
                return Property
        return ''

main(input_file_name, output_file_name)
