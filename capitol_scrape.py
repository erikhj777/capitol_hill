#!/usr/bin/env python3

#run this script to update master arrests csv file w/ new entries

import sys
import requests as r
import bs4
import lxml
import csv
import pandas as pd
from pprint import pprint
import numpy

#URL for the DoJ webpage with info on the capital arrests
base_URL = "https://www.justice.gov/usao-dc/capitol-breach-cases"
#URL for RSS feed of the capital requests
RSS_feed = "https://www.justice.gov/rss/defendants/185846"

def main():

    response = r.get(base_URL) #HTML GET request for the target site
    #check HTML GET request status code
    if response.status_code == 200:
        print('GET request successful!')
    else:
        print('GET request unsuccessful!')
        sys.exit()

    #parse the response results as HTML w/ BeautifulSoup
    #first parameter is HTML source file, 2nd param is the parser
    html_soup = bs4.BeautifulSoup(response.text, 'lxml')

    #are 3 container classes for results: 'odd views-row-first' 'even' 'odd'
    #.find_all method returns a result set object with the specified parameters
    rs1 = html_soup.find_all('tr', class_ = 'odd views-row-first')
    rs2 = html_soup.find_all('tr', class_ = 'even')
    rs3 = html_soup.find_all('tr', class_ = 'odd')

    defendants_container = rs1 + rs2 + rs3 #concatanate all results into a list
    #print(defendants_container[0].prettify()) #.pretify() is pprint for HTML
    print(f'{len(defendants_container)} total defendant records found')

    #read in existing arrest records in CSV file as pandas df
    df = pd.read_csv('/Users/eojohnson/Documents/Army Extremism/Research/New Script/capitol_arrests.csv')

    new_entry_count = 0

    for each in defendants_container:

        #relevant attribute tags for extraction
        #Case Number
        case_num = each.find('td', class_ = 'views-field views-field-field-case-multi-number').text
        #Name
        name = each.find('td', class_ = 'views-field views-field-title active').text
        #Charges
        charges = each.find('td', class_ = 'views-field views-field-field-case-multi-charges').text
        #Location of arrest
        location = each.find('td', class_ = 'views-field views-field-field-case-multi-location').text
        #case status
        case_status = each.find('td', class_ = 'views-field views-field-field-case-multi-status').text
        #entry last Updated
        last_update = each.find('td', class_ = 'views-field views-field-changed').text

        #case numbers not unique, sometime multiple defendants tried under same case number?
        #use arrestee name to identify unique entries
        if name in df.values:
            continue
        elif name not in df.values:

            #format data for ea entry into pd series
            new_entry = {
                    'case_num' : case_num,
                    'name' : name,
                    'charges' : charges,
                    'location' : location,
                    'case_status' : case_status,
                    'last_update' : last_update,
                    'notes' : 'none'
                    }

            new_entry_count += 1

            df = df.append(new_entry, ignore_index = True)

    #write the df back to the csv file
    df.to_csv('/Users/eojohnson/Documents/Army Extremism/Research/New Script/capitol_arrests.csv', index = False)

    print(f'search complete, {new_entry_count} new entry(s) added')

if __name__ == "__main__":
    main()
