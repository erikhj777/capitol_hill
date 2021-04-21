#!/usr/bin/env python3

import requests as r
import bs4
import lxml
import sys
import os
from datetime import date
import re

#URL for the DoJ webpage with info on the capital arrests
base_URL = "https://www.justice.gov/usao-dc/capitol-breach-cases"
doc_base_URL = 'https://www.justice.gov'

def main():

    response = r.get(base_URL) #HTML GET request for the target site

    if response.status_code == 200: #check HTML GET request status code
        print('GET request successful!')
    else:
        print('GET request unsuccessful!')
        sys.exit()

    #parse the response results as HTML w/ BeautifulSoup
    #first parameter is HTML source file, 2nd param is the parser
    html_soup = bs4.BeautifulSoup(response.text, 'lxml') #lxml is the parser

    #are 2 container classes for results: 'odd' and 'even'
    #.find_all method returns a result set object with the specified parameters
    rs1 = html_soup.find_all('tr', class_ = 'odd')
    rs2 = html_soup.find_all('tr', class_ = 'even')

    defendants_container = rs1 + rs2 #html container of all unique defendants

    #create parent directory to hold all search results
    parent_path = f'/Users/eojohnson/Documents/Army Extremism/Research/New Script/doc_pulls/{date.today()}'
    try:
        os.mkdir(parent_path)
    except FileExistsError:
        print('Data pull already run for today! \nNo new dir will be created!')
        sys.exit()

    folders_created = 0 #start a running count of all the new defendants identified
    docs_created = 0 #start a running count of all the new docs downloaded

    #identify a starting point for the directory walk
    root_dir = '/Users/eojohnson/Documents/Army Extremism/Research/New Script/doc_pulls'
    extant_dirs = [] #create an empty container to hold all extant dirs

    for root, dirs, files in os.walk(root_dir, topdown=False):
        for each in dirs: #iterate through all directories found
            #append the name of that dir to get a list of all extant dirs
            extant_dirs.append(each)

    for each in defendants_container: #loop through each individual defendants

        #make a name for the subfolder to hold docs for this defendant
        name = each.find('td', class_ = 'views-field views-field-title active').text
        name = name.strip(' \n') #remove all spaces & newline chars from lead & trail

        if name not in extant_dirs: #check if a dir already exists for this defendant
            os.mkdir(parent_path + '/' + name)
            print(f'New directory created for {name}')
            folders_created += 1 #increase created_count by 1 for a new dir created

            #loops through each file <span> tag with an associated 'file' class
            for i in each.find_all('span', class_ = 'file'):

                text = str(i.a) #retrive the text inside the <a> tag
                #re pattern to return text inside the first set of "", this is the url extension
                pattern = r'"([A-Za-z0-9_\./\\-]*)"'
                m = re.search(pattern, text) #search for 1st instance of that pattern within the <a> tag text
                complete_url = doc_base_URL + m.group().strip('\"') #combine base url w/ extension

                #now preform the GET request for that doc
                new_doc = r.get(complete_url) #GET requests for URL returns a 'response-type' object
                docs_created += 1 #increase the overall count for the number of docs downloaded
                print(f'File found, download successful! {docs_created} total collected!') #.content attribute for PDF file is binary
                with open (f'{parent_path}/{name}/{docs_created}.pdf', 'wb') as f: #need to specify write binary
                    f.write(new_doc.content)
        else:
            print('Folder already exists!')

    print(f'{folders_created} new defendant folders created!')
    print(f'{docs_created} new files downloaded!')

if __name__ == '__main__':
    main()
