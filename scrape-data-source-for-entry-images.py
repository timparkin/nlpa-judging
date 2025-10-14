import pandas as pd
import requests
import os
import math
from pathlib import Path
import sys
import tempfile
import shutil
from urllib.parse import urlparse
from posixpath import basename, dirname
# This is the code that gets the images from the data storage which should be the server in this case
# We need a source csv, a sample of which is in this folder

# Print iterations progress
def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='█', printEnd="\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


try:
    # get the target folder
    base = sys.argv[1]
    # get the source csv file e.g. '~/all_images_from_server.csv'
    source_csv = sys.argv[2]
except:
    directory = os.getcwd()
    base = '/Volumes/X94T_2025/NLPA-2025/nlpa-2025/ORIGINALS'
    source_csv = os.path.join(directory, 'nlpaentries.csv')


# Get a temporary directory
tmp_directory = tempfile.gettempdir()

def save_photo_from_url(url, filename, category, directory, id):
    # print('%s : %s %s'%(id, filename, directory))
    target_directory = os.path.join(base, category, directory)
    Path(target_directory).mkdir(parents=True, exist_ok=True)
    target_filename = os.path.join(target_directory, filename)
    tmp_filename = os.path.join(tmp_directory, filename)
    if not os.path.isfile(target_filename):
        with open(tmp_filename, 'wb') as handle:
            response = requests.get(url, stream=True)

            if not response.ok:
                print(response)

            for block in response.iter_content(1024):
                if not block:
                    break

                handle.write(block)
        shutil.copy(tmp_filename, target_filename)
        os.remove(tmp_filename)
    else:
        print('-- Skipping %s'%filename)

df = pd.read_csv(source_csv)

space = 0
for i in range(len(df)):

    printProgressBar(i + 1, len(df), prefix = 'Progress:', suffix = 'Complete', length = 80)

    row = df.loc[i]
    url = 'https://submit.naturallandscapeawards.com/%s'%row['entry_url']
    parse_object = urlparse(url)
    noclash_filename = basename(parse_object.path)


    id = row['entry_id']
    user_id = int(row['id'])
    if not isinstance(url,str):
        continue
    filename = str(row['entry_filename'])
    if 'entries' in filename:
        filename = filename.split('/')[-1]
    name = row['name']
    size = row['entry_photo_size']
    category = row['entry_category']
    if not isinstance(category, str):
        category = 'undefined'

    if not math.isnan(size):
        space += size
        save_photo_from_url(url, noclash_filename, category, name, id)
        # print('{:=4.1f}Mb'.format(int(size/100000)/10))

print('{:=4.1f}Mb'.format(int(space/100000000)/10))
