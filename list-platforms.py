# Simple script to read target data from targets.json and spreadsheet

import requests
import os
import urllib, json
import time
import openpyxl.styles
from argparse import ArgumentParser
from prettytable import PrettyTable
from natsort import natsorted
from dotenv import load_dotenv
from openpyxl import Workbook
from openpyxl.utils import get_column_letter
from openpyxl import load_workbook
from progress.bar import IncrementalBar

url_os_mbed_com = 'https://os.mbed.com/api/v3/platforms/'
# master
url_targets_json = 'https://raw.github.com/ARMmbed/mbed-os/master/targets/targets.json'
# url_targets_json = 'https://raw.githubusercontent.com/MarceloSalazar/mbed-os/platform_cleanup3/targets/targets.json'


# Ignore non-valid targets from targets.json
targets_ignore = ["TARGET", "PSA_TARGET", "NSPE_TARGET", "SPE_TARGET", "CM4_UARM", "CM4_ARM", \
                  "CM4F_UARM", "CM4F_ARM", "__BUILD_TOOLS_METADATA__"]
os_mbed_com_data = {}
spreadsheet_file = ''


def get_target_os_mbed_com():
    #global os_mbed_com_data
    targets = {}
    # Read data from os.mbed.com and crete local database
    # TODO: use user/pass using dotenv info
    response = requests.get(url_os_mbed_com,auth=('user', 'password'))
    db = response.json()

    print("Print targets...\n")
    # Iterate through os.mbed.com targets 
    for i in range(len(db)):
        target = {}
        target['name'] = db[i]['logicalboard']['name'].upper()
        print(target['name'])
        
        target['vendor'] = db[i]['vendor']['name'].upper()
        target['mbed-enabled'] = db[i]['features'][0]['category']['name']
        target['mbed5'] = 'N'
        target['mbed2'] = 'N'
        target['pelion'] = 'N' # search for Mbed Enabled Pelion Ready
        os_version = []
        
        for j in db[i]['features']:
            if j['category']['name'] == "Mbed OS support":
                if "5" == j['name'].strip('Mbed OS ')[0]:
                    target['mbed5'] = 'Y'
                elif "2" == j['name'].strip('Mbed OS ')[0]:
                    target['mbed2'] = 'Y'  
                    
        targets[i] = target
    return targets



def print_table(db):
    global targets_json
    table_header = ['#', 'Name', 'Target', 'targets.json', 'Mbed Enabled', 'Ext', 'Mbed OS']

    table = PrettyTable(table_header)
    table.align['#'] = 'r'
    table.align['Name'] = 'l'
    table.align['Mbed OS'] = 'l'
    count = 1

    # Iterate through os.mbed.com targets 
    for i in range(len(db)):
        if db[i]['features'][0]['category']['name'] == "Mbed Enabled":
            mbedenabled = 'y'
        else:
            mbedenabled = ''

        target = db[i]['logicalboard']['name'].upper()
        if target in targets_json_list:
            targets_json = 'y'
        else:
            targets_json = ''

        # Find Mbed OS version
        os_version = []
        for j in db[i]['features']:
            if j['category']['name'] == "Mbed OS support":
                os_version.append(j['name'].strip('Mbed OS '))
        os_version = natsorted(os_version)[::-1]
        os_version = ", ".join(map(str, os_version))

        # Filter by vendor
        if args.vendor is not None:
            if db[i]['logicalboard']['vendor']['name'].upper() == str(args.vendor).upper():
                table.add_row([count, db[i]['name'], \
                target, targets_json, mbedenabled, '', os_version])
                count += 1

        # Filter by platform
        elif args.platform is not None:
            if db[i]['vendor']['name'].upper() == str(args.platform).upper():
                table.add_row([count, db[i]['name'], \
                        target, targets_json, mbedenabled, '', os_version])
                count += 1

        # Show all vendor/platforms
        else: 
            if target in ext_file_memory:
                external = 'y'
            else:
                external = 'n'

            table.add_row([count, db[i]['name'], \
                    target, targets_json, mbedenabled, \
                    external, os_version ])
        
            count += 1

    if args.vendor is None and args.platform is None: 
        # Check other targets that are NOT in the online database
        for i in targets_json_list:
            in_flag = 0
            for j in range(len(db)):
                if i in db[j]['logicalboard']['name'].upper():
                    in_flag = 1
                    break

            if in_flag == 0:
                if i in ext_file_memory:
                    external = 'y'
                else:
                    external = 'n'
    
                table.add_row([count, '?', \
                        i, 'y', '?', external, '?'])
                count += 1

    print(table)


def check_missing_targets_json():
    """ Check missing items in targets.json and prints     

    Returns:    
    none
    
    """

    if spreadsheet_file == '':
        print("Spreadsheet not found")

    # Open spreadsheet
    try:
        wb = load_workbook(filename = spreadsheet_file)
        ws = wb['Data']

    except:
        print("Could not find '.xlsx' in the current directory. Skipping check.")
        return targets
   
    print("\nCheck missing items in spreadsheet")

    bar = IncrementalBar('Processing', max=ws.max_row)

    missing_targets = []
    for row in range(2, ws.max_row):
        #if ws.cell(row=row, column=1).value != None:
        #partner = ws.cell(row=row, column=1).value

        target = ws.cell(row=row, column=3).value
    
        if target.upper() in targets_json:
            pass
        else:
            missing_targets.append(str(target).upper())
        bar.next()
    
    print('\n')
    print(missing_targets)

# Download target list from targets.json and check public field
def get_targets_json():
    
    targets_json = []
    res = requests.get(url_targets_json)
    db = res.json()

    bar = IncrementalBar('Processing', max=len(db))

    print("\nRead targets from targets.json")
    # Check if target public is set (public=true), or not set (public!=false)
    for i in db:  
        # Check if targets are not public
        #if 'public' in db[i] and db[i]['public'] == False:
        #    continue
        targets_json.append(str(i).upper())
        bar.next()

    print("\n")
    return targets_json  

def get_target_spreadsheet():
    """ Returns a list of known targets in the spreadsheet       

    Returns:    
    A list of targets
    
    """

    if spreadsheet_file == '':
        print("Spreadsheet not found\n")

    targets = []

    # Open spreadsheet
    try:
        wb = load_workbook(filename = spreadsheet_file)
        ws = wb['Data']

    except:
        print("Could not find '.xlsx' in the current directory. Skipping check.")
        return targets
   
    print("\nRead targets from spreadsheet")
    bar = IncrementalBar('Processing', max=ws.max_row)

    for row in range(2, ws.max_row+1):
        target = ws.cell(row=row, column=3).value
        targets.append(target.upper())
        bar.next()

    print("\n")
    return targets

def check_missing_items():

    targets_json = get_targets_json()
    targets_spreadsheet = get_target_spreadsheet()

    print("\nMissing items in targets.json")
    for i in targets_spreadsheet:
        missing = 1
        for j in targets_json:
            if i == j:
                missing = 0
        if missing == 1:
            print(i)

    print("\nMissing items in spreadsheet")
    for i in targets_json:
        if i in targets_ignore:
            continue
        missing = 1
        for j in targets_spreadsheet:
            if i == j:
                missing = 0
        if missing == 1:
            print(i)

def update_spreadsheet():

    targets_json = get_targets_json()
    targets_spreadsheet = get_target_spreadsheet()

    # Open spreadsheet
    try:
        wb = load_workbook(filename = spreadsheet_file)
        ws = wb['Data']

    except:
        print("Could not find '.xlsx' in the current directory. Skipping check.")
        return
   
    print("\nUpdate spreadsheet")
    bar = IncrementalBar('Processing', max=ws.max_row)

    for row in range(2, ws.max_row+1):
        target = str(ws.cell(row=row, column=3).value).upper()

        missing = 1
        for j in targets_json:
            if target == j:
                missing = 0

        if missing == 1:
            ws.cell(row=row, column=14).value = "N"
        else:
            ws.cell(row=row, column=14).value = "Y"

        bar.next()

    # Save spreadsheet (requires file to be closed elsewhere)
    wb.save(filename = spreadsheet_file)

def main():

    global args
    global os_mbed_com_data
    global spreadsheet_file

    # Parser handling
    parser = ArgumentParser(description="Data parser from os.mbed.com/platforms")
    
    parser.add_argument(
        '-m', '--missing', dest='missing',
        action='store_const', const=1, default=0,
        help='Check missing items', required=False)

    parser.add_argument(
        '-u', '--update', dest='update',
        action='store_const', const=1, default=0,
        help='Update spreadsheet', required=False)

    parser.add_argument(
        '-v', '--vendor', dest='vendor',
        help='Regular expression to filter platform by vendor', required=False)

    parser.add_argument(
        '-f', '--file', dest='file',
        help='Text file to check if target is listed there', required=False)

    args = parser.parse_args()

    # Load spreadsheet
    if args.file:
        spreadsheet_file = args.file

    # Check missing items
    if args.missing:
        print("Checking missing items...")
        check_missing_items()

    if args.update:
        print("Update spreadsheet...")
        update_spreadsheet()

    get_target_os_mbed_com()

    exit(0)

if __name__ == "__main__":
    main()