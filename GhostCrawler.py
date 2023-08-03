import argparse
import csv
import math
import os
import re
import time
from datetime import datetime
from multiprocessing import Pool, cpu_count, freeze_support
from urllib.parse import unquote, quote

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from functools import reduce

# Global variables
filename = "$SEARCH_results_$DATE.csv"
proxies = {"http": "socks5h://localhost:9050", "https": "socks5h://localhost:9050"}
field_delim = ','

# Supported dark web search engines
supported_engines = {
    'ahmia': "http://msydqstlz2kzerdg.onion/",
    'darksearchenginer': "http://darksearchioeagkg2.onion/",
    'darksearchio': "http://darksearchio7odl64.onion/",
    'deeplink': "http://gjobqjj7wyczbqie.onion/",
    'evosearch': "http://bznjtqphs2lp4xdd.onion/",
    'haystack': "http://haystakvxad7wbk5.onion/",
    'multivac': "http://multivacigqzqqon.onion/",
    'notevil': "http://zlal32teyptf4tvi.onion/",
    'onionland': "http://3bbad7fauom4d6sgppalyqddsqbf5u5p56b5k5uk2zxsy3d6ey2jobad.onion/",
    'onionsearchengine': "http://5u56fjmxu63xcmbk.onion/",
    'onionsearchserver': "http://darkf6l4nywtlx47.onion/",
    'phobos': "http://phobosxilamwcg75xt22id7aywkzol6q6rfl2flipcqoc4e4ahima5id.onion/",
    'tor66': "http://tor66sezptuu2nta.onion/",
    'tordex': "http://tordex7iie7z2wcg.onion/",
    'torgle': "http://torglecnwuglf2gmyox3obsm3gvmzz4tds3ljkdasr23ed2dyprlqd.onion/",
    'torgle1': "http://torgleklr4i7yzh4.onion/",
    'tormax': "http://tormaxunodsbvtgo.onion/",
}

# Helper function to clear text
def clear(text):
    return re.sub(r"\s{2,}|\n", "", text)

# Helper function to get a parameter from a URL
def get_parameter(url, param):
    param_re = re.match(r".*{}=([^&]+).*".format(param), url)
    if param_re is not None:
        return param_re.group(1)
    return None

# Helper function to find sensitive information from text
def find_sensitive_info(text):
    # Regular expressions for email addresses, phone numbers, and IP addresses
    email_regex = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    phone_regex = r"\b(?:\+\d{1,3}[- ]?)?\d{10}\b"
    ip_regex = r"\b(?:\d{1,3}\.){3}\d{1,3}\b"

    email_addresses = re.findall(email_regex, text)
    phone_numbers = re.findall(phone_regex, text)
    ip_addresses = re.findall(ip_regex, text)

    return email_addresses, phone_numbers, ip_addresses

# The dark web search engines' scraping functions (Part 3)

# ... (The code for the functions onionsearchengine, tordex, tor66, tormax, haystack, multivac is the same as in Part 3)

# The main web scraping function (Part 4)

# ... (The code for the functions evosearch, deeplink, torgle1, get_domain_from_url, link_finder is the same as in Part 4)

# Function to run a specific web scraping method (Part 5)
def run_method(method_name_and_argument):
    method_name = method_name_and_argument.split(':')[0]
    argument = method_name_and_argument.split(':')[1]
    ret = []
    try:
        ret = globals()[method_name](argument)
    except Exception as e:
        print(f'Exception occurred: {e}')
    return ret

# Helper function to write data to CSV file
def write_to_csv(csv_writer, data):
    csv_writer.writerow([
        data.get('engine', ''),
        data.get('title', ''),
        data.get('url', ''),
        data.get('description', ''),
        data.get('email_addresses', ''),
        data.get('phone_numbers', ''),
        data.get('ip_addresses', '')
    ])

# The main web scraping script (Part 6)
def scrape():
    global filename

    start_time = datetime.now()

    # Building the filename
    filename = str(filename).replace("$DATE", start_time.strftime("%Y%m%d%H%M%S"))
    search = str(args.search).replace(" ", "")
    if len(search) > 10:
        search = search[0:9]
    filename = str(filename).replace("$SEARCH", search)

    func_args = []
    stats_dict = {}
    if args.engines and len(args.engines) > 0:
        eng = args.engines[0]
        for e in eng:
            try:
                if not (args.exclude and len(args.exclude) > 0 and e in args.exclude[0]):
                    func_args.append("{}:{}".format(e, args.search))
                    stats_dict[e] = 0
            except KeyError:
                print("Error: search engine {} not in the list of supported engines".format(e))
    else:
        for e in supported_engines.keys():
            if not (args.exclude and len(args.exclude) > 0 and e in args.exclude[0]):
                func_args.append("{}:{}".format(e, args.search))
                stats_dict[e] = 0

    # Doing multiprocessing
    if args.mp_units and args.mp_units > 0:
        units = args.mp_units
    else:
        # Use (cores count - 1), but not less than one, threads
        units = max((cpu_count() - 1), 1)
    print("search.py started with {} processing units...".format(units))
    freeze_support()

    results = {}
    with Pool(units) as p:
        results_map = p.map(run_method, func_args)
        results = reduce(lambda a, b: a + b if b is not None else a, results_map)

    stop_time = datetime.now()

    if not args.continuous_write:
        with open(filename, 'w', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=field_delim, quoting=csv.QUOTE_ALL)
            for r in results:
                write_to_csv(csv_writer, r)

    total = 0
    print("\nReport:")
    print("  Execution time: %s seconds" % (stop_time - start_time))
    print("  Results per engine:")
    for r in results:
        stats_dict[r['engine']] += 1
    for s in stats_dict:
        n = stats_dict[s]
        print("    {}: {}".format(s, str(n)))
        total += n
    print("  Total: {} links written to {}".format(str(total), filename))

# Main script
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Dark web search engine scraper.')
    parser.add_argument('search', metavar='SEARCH_TERM', type=str, help='The search term for the dark web.')
    parser.add_argument('--engines', nargs='*', action='append', help='Specify the search engines to use.')
    parser.add_argument('--exclude', nargs='*', action='append', help='Specify the search engines to exclude.')
    parser.add_argument('--mp_units', type=int, help='Specify the number of multiprocessing units to use.')
    parser.add_argument('--continuous_write', action='store_true', help='Enable continuous writing to the CSV file.')
    args = parser.parse_args()

    # Check if at least one engine is specified
    if not args.engines or len(args.engines[0]) == 0:
        print("Error: At least one search engine must be specified.")
    else:
        scrape()