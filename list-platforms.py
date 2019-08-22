# Simple script to read data from os.mbed.com/platforms

import requests
import urllib, json
from argparse import ArgumentParser
from prettytable import PrettyTable
from natsort import natsorted

url_os_mbed_com = 'https://os.mbed.com/api/v3/platforms/'

# Read data from os.mbed.com and crete local database
response = requests.get(url_os_mbed_com,auth=('user', 'password'))
data = response.json()

def print_table(db):

    table_header = ['#', 'Name', 'Target', 'Mbed Enabled', 'Mbed OS']

    table = PrettyTable(table_header)
    table.align['#'] = 'r'
    table.align['Name'] = 'l'
    table.align['Mbed OS'] = 'l'
    count = 1

    for i in range(len(db)):
        if db[i]['features'][0]['category']['name'] == "Mbed Enabled":
            mbedenabled = 'y'
        else:
            mbedenabled = ' '
        
        if args.vendor is not None:
            if db[i]['logicalboard']['vendor']['name'].upper() == str(args.vendor).upper():
                os_version = []
                for j in db[i]['features']:
                    if j['category']['name'] == "Mbed OS support":
                        os_version.append(j['name'].strip('Mbed OS '))
                
                os_version = natsorted(os_version)[::-1] 
                table.add_row([count, db[i]['name'], \
                db[i]['logicalboard']['name'].upper(), mbedenabled, \
                ", ".join(map(str, os_version)) ])
                count += 1
        elif args.platform is not None:
            if db[i]['vendor']['name'].upper() == str(args.platform).upper():
                os_version = []
                for j in db[i]['features']:
                    if j['category']['name'] == "Mbed OS support":
                        os_version.append(j['name'].strip('Mbed OS '))
                        
                os_version = natsorted(os_version)[::-1] 
                table.add_row([count, db[i]['name'], \
                        db[i]['logicalboard']['name'].upper(), mbedenabled, \
                        ", ".join(map(str, os_version)) ])
                count += 1

    print table


def main():

    global args
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
        '-f', '--filter', dest='filter',
        help='Regular expression to filter platform name', required=False)

    # Parse/run command
    #if len(argv) <= 1:
    #    parser.print_help()
    #    exit(1)

    args = parser.parse_args()

    # Print all data by default
    print_table(data)

    # Write output in file
    #if args.output is not None:
    #    returned_string = generate_output()
    #else:  # Write output in screen
    #    returned_string = memap.generate_output(args.export, depth)

    exit(0)

if __name__ == "__main__":
    main()
