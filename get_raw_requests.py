import pandas as pd
import requests
import os
import math
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw
import codecs
import random
import string
import base64
import statistics as S
import pyexiv2
import logging
import shutil
#from userauth.models import CustomUser as User, Year

# from portfolio import port_ids, scores_dict
#
# port_data = {}
# port_id_list = []
# for r in port_ids:
#     #print(int(r[0]),r[1])
#     port_data[int(r[0])] = r[1]
#     port_id_list.append(int(r[0]))
#
# port_scores_by_entry_id = {}
# for user_id, score_data in scores_dict.items():
#     for entry_id, score in score_data['items'].items():
#         port_scores_by_entry_id[int(entry_id)] = float(score)

#print(port_scores_by_entry_id)
#print('==========')
#print('11547 in %s'%(11547 in port_scores_by_entry_id.keys()))

import io
from PIL import Image
from PIL import ImageCms
import sys


# We need to ouput the following
# name	category	email	id	entry_id	filename	Url

# Print iterations progress
def printProgressBar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\r"):
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
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end = printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


# directory is used as base for target and source
# source should be the raw downloads, target the directory to place the scored images in

try:
    directory=sys.argv[1]
    source = sys.argv[2]
except:
    directory = os.getcwd()
    source = '/Volumes/NLPA 2022/2024/ORIGINALS'

root_directory = directory

label_lookup = {
5: 'Red',
4: 'Yellow',
3: 'Green',
2: 'Blue',
1: 'Purple',
0: 'Grey',
}


category_lookup = {
'GS': 'Grand Scenic',
'IL': 'Intimate Landscape',
'AD': 'Abstract and Details',
'P1': 'Project',
'P2': 'Project',
}

folder_lookup = {
'1 - Grand Scenic': 'GS',
'2 - Intimate Landscape': 'IL',
'3 - Abstract and Details': 'AD',
}

category_reverse_lookup = {}
for key, value in category_lookup.items():
    category_reverse_lookup[value] = key





base = os.path.join(directory, source)
target = os.path.join(directory,'data')
logging.info('source directory = %s'%base)
logging.info('target directory = %s'%target)

df = pd.read_csv('data/nlpaentries.csv')



lookup = {}
l = len(df)
for i in range(l):
    # printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 80)
    row = df.loc[i]
    url = 'https://submit.naturallandscapeawards.com/%s'%row['entry_url']
    id = row['id']
    entry_id = row['entry_id']

    if not isinstance(url,str):
        print(id, filename,url)
        continue
    filename = str(row['entry_filename'])
    if 'entries' in filename:
        filename = filename.split('/')[-1]
    name = row['name']
    email = row['email']
    category = row['entry_category']
    size = row['entry_photo_size']
    if category == 'undefined':
        continue
    if not isinstance(category, str):
        # print(filename,category)
        logging.debug('category %s not string'%category)
        continue
    if not math.isnan(entry_id) and int(entry_id) == 51709:
        print(id, filename, url)
        print(row)
    if not math.isnan(size):
        lookup[entry_id] = {'id':id, 'entry_id': entry_id, 'name':name, 'category':category_lookup[category], 'email':email, 'filename': filename, 'Url': url}
    else:
        # print(filename,size)
        pass


df = pd.read_csv('data/jblistview_nlpa_second_round_entries.csv')
l = len(df)
entries = []
for i in range(l):
    row = df.loc[i]
    filename = row['File,name']
        
    if filename == '00_project_description.jpg':
        continue


    try:
        code, id, entry_id = filename[:-4].split('__')
    except ValueError:
        sys.exit()

    if int(entry_id) == 51709:
        print(id, filename, url)
        print(row)


    entry = lookup[int(entry_id)]
    if row['Folder'] in folder_lookup:
        entry['category'] = folder_lookup[row['Folder']]
    entries.append(entry)

# The code on the server, update_raw_status.py, only uses the ID for adding the second round info.
# However, this code is also used to email people about their entries (

df = pd.DataFrame.from_dict(entries)
df = df[['name','category','email','id','entry_id','filename','Url']]
df.to_csv('data/nlpa_second_round_entries.csv', index=False)

# for email in list(set(emails)):
#     print(email)





#for user in users:
#    if 'Parkin' in user.last_name:
#        print('%s %s (%s)'%(user.last_name, user.first_name, user.id))
#        u = user
    # u = User.objects.get(id=1623)
    # entries = u.entry_set.all()
