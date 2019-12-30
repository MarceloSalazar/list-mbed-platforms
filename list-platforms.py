# Simple script to read data from os.mbed.com/platforms

import requests
import urllib, json
from argparse import ArgumentParser
from prettytable import PrettyTable
from natsort import natsorted

url_os_mbed_com = 'https://os.mbed.com/api/v3/platforms/'
url_targets_json = 'https://raw.github.com/ARMmbed/mbed-os/master/targets/targets.json'

# Store name of targets from targets.json
targets_json_list = []
os_mbed_com_data = {}
ext_file_memory = ''

def load_ext_file():
    global ext_file_memory
    if args.file:
        try:
            with open(args.file, 'r') as file_input:
                for line in file_input:
                    ext_file_memory = ext_file_memory + line.upper()
        except IOError as error:
            print("I/O error({0}): {1}".format(error.errno, error.strerror))
            return False

# Download target list from targets.json and check public field
def download_targets_json():
    global targets_json_list
    res = requests.get(url_targets_json)
    db = res.json()
    
    # Check if target public is set (public=true), or not set (public!=false)
    for i in db:  
        if 'public' in db[i] and db[i]['public'] == False:
            continue
        targets_json_list.append(str(i).upper())
        
def download_os_mbed_com():
    global os_mbed_com_data
    # Read data from os.mbed.com and crete local database
    response = requests.get(url_os_mbed_com,auth=('user', 'password'))
    os_mbed_com_data = response.json()

def print_table(db):
    global targets_json
    table_header = ['#', 'Name', 'Target', 'targets.json', 'Mbed Enabled', 'Mbed OS', 'Ext']

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
                target, targets_json, mbedenabled, os_version])


        # Filter by platform
        elif args.platform is not None:
            if db[i]['vendor']['name'].upper() == str(args.platform).upper():
                table.add_row([count, db[i]['name'], \
                        target, targets_json, mbedenabled, os_version])


        # Show all vendor/platforms
        else: 
            if target in ext_file_memory:
                external = 'y'
            else:
                external = 'n'

            table.add_row([count, db[i]['name'], \
                    target, targets_json, mbedenabled, \
                    os_version, external ])
        
        count += 1

    # Check other targets that are NOT in the online database
    for i in targets_json_list:
        in_flag = 0
        for j in range(len(db)):
            if i in db[j]['logicalboard']['name'].upper():
                in_flag = 1
                break

        if in_flag == 0:
            table.add_row([count, '?', \
                    i, 'y', '?', '?', 'tbd'])
            count += 1

    print table


def main():

    global args
    global os_mbed_com_data

    # Parser handling
    parser = ArgumentParser(description="Data parser from os.mbed.com/platforms")

    parser.add_argument(
        '-m', '--mbed-enabled', dest='mbed-enabled',
        action='store_const', const=0, default=0,
        help='Display only Mbed Enabled platforms', required=False)
    
    parser.add_argument(
        '-2', '--mbed2', dest='mbed2',
        action='store_const', const=0, default=0,
        help='Display only Mbed 2 platforms', required=False)

    parser.add_argument(
        '-5', '--mbed5', dest='mbed5',
        action='store_const', const=0, default=0,
        help='Display only Mbed OS 5 platforms', required=False)

    parser.add_argument(
        '-p', '--platform', dest='platform',
        help='Regular expression to filter platform by platform', required=False)

    parser.add_argument(
        '-v', '--vendor', dest='vendor',
        help='Regular expression to filter platform by vendor', required=False)

    parser.add_argument(
        '-f', '--file', dest='file',
        help='Text file to check if target is listed there', required=False)

    args = parser.parse_args()

    if args.file:
        load_ext_file()

    # Download targets.json
    download_targets_json()

    # Download data from os.mbed.com
    download_os_mbed_com()

    # Print data
    print_table(os_mbed_com_data)

    # Write output in file
    #if args.output is not None:
    #    returned_string = generate_output()
    #else:  # Write output in screen
    #    returned_string = memap.generate_output(args.export, depth)

    exit(0)

if __name__ == "__main__":
    main()