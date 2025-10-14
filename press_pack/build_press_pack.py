

import pandas as pd
import requests
import os
import math
from pathlib import Path
import sys
import argparse
import yaml
from pprint import pprint
import csv
import shutil

# DONT FORGET TO CHANGE THIS!! 
target_directory = '/mnt/nlpa/nlpa-press-2025'

from pathlib import Path

def find_files(base_dir, search_string):
    base = Path(base_dir)
    return [p for p in base.rglob("*") if p.is_file() and search_string in p.name]

def get_file_path(id, entry_id, filename, image_directory):

    src_filename = f"{entry_id[::-1]}__{id}__{entry_id}.jpg"

    test_grand = os.path.join(image_directory, '1 - Grand Scenic', src_filename)
    test_intimate = os.path.join(image_directory, '2 - Intimate Landscape', src_filename)
    test_abstract = os.path.join(image_directory, '3 - Abstract and Details', src_filename)


    if os.path.isfile(test_grand):
        return test_grand
    if os.path.isfile(test_intimate):
        return test_intimate
    if os.path.isfile(test_abstract):
        return test_abstract


    files = find_files( os.path.join(image_directory, '4 - Project'), src_filename )
    if len(files) == 1:
        return files[0]

    files = find_files(os.path.join(image_directory, 'portfolio'), src_filename)
    if len(files) == 1:
        return files[0]

    print('failed',entry_id)


def copy_images(id, entry_id, category, image_directory, filename, output_item, entrant, winner, row):

    f = get_file_path(id, entry_id, filename, image_directory)

    target = os.path.join(target_directory, filename)

    os.makedirs(os.path.dirname( target ), exist_ok=True)

    shutil.copy(f, target)












fields = "Name,Award,Photo ID,Nationality,Bio,Profile Link Type,Profile Link,Title,Caption".split(',')

winners_fields = "category,id,entry_id,filename,url,prize,name,email,country,facebook,instagram,website,bio".split(',')

entrants_fields = """Timestamp
Your Name (e.g. John Henry-Smythe, Arya Kumar, Zhang Chen)
Where you live
Profile
Type of Profile Link
Profile Link
Your Photo ID
Photograph Title
Press Info""".splitlines()


specials = {
    'M': 'Mountains',
    'WL': 'Woodland',
    'TL': 'Tropical Landscapes',
    'S': 'Seascapes',
    'RG': 'Rocks and Geology',
    'IB': 'In Your Backyard',
    'FW': 'Frozen Worlds',
    'DL': 'Desert Landscapes',
}

categories = {
    'Scenic': 'Landscape',
    'and Details': 'Landscapes',
    'GS': 'Grand Landscape',
    'IL': 'Intimate Landscape',
    'AD': 'Abstract Landscapes',
}

def replace_from_specials(text: str) -> str:
    """
    Replaces all occurrences of dictionary keys in the given text
    with their corresponding values.

    Args:
        text (str): The input string.
        replacements (dict): Dictionary with {key: value} pairs to replace.

    Returns:
        str: The updated string with replacements applied.

        M, Runner Up
    """
    if len(text) > 2:
        return text
    for key, value in specials.items():
        text = text.replace(key,str(value))
    return text.strip()

def replace_from_category(text: str) -> str:
    """
    Replaces all occurrences of dictionary keys in the given text
    with their corresponding values.

    Args:
        text (str): The input string.
        replacements (dict): Dictionary with {key: value} pairs to replace.

    Returns:
        str: The updated string with replacements applied.

        M, Runner Up
    """
    text = text.strip()
    for key, value in categories.items():
        text = text.replace(key,str(value))
    return text

specials_index = 'M,WL,TL,S,RG,IB,FW,DL'.split(',')

positions = {
    "Highly Commended": "4 Highly Commended",
    "Winner": "1 Winner",
    "Runner Up": "2 Runner Up",
    "Second": "2 Second",
    "Third Place": "3 Third Place",
    "Fourth": "4 Fourth",
    "Fifth": "5 Fifth",
    "Sixth": "6 Sixth",
    "Photograph of the Year": "00 Photograph of the Year",
}
def replace_from_position(text: str) -> str:
    """
    Replaces all occurrences of dictionary keys in the given text
    with their corresponding values.

    Args:
        text (str): The input string.
        replacements (dict): Dictionary with {key: value} pairs to replace.

    Returns:
        str: The updated string with replacements applied.

        M, Runner Up
    """

    for key, value in positions.items():
        text = text.replace(key,str(value))
    return text

def normalize(v):
    if isinstance(v, tuple) and len(v) == 1:
        return v[0]
    return v

if __name__ == "__main__":


    with open('../config.yaml') as f:
         yaml_data = yaml.safe_load(f)

    yaml_args = yaml_data['args']
    fullcsv = "../data/nlpaentries.csv"
    image_directory = yaml_args['target_base'].replace('Primary','Primary (grade all)')


    row_by_entry_id={}

    df = pd.read_csv(fullcsv)
    l = len(df)

    for i in range(l):
        row = df.loc[i]
        if math.isnan(row['id']):
            continue

        entry_id = str(int(row['entry_id']))
        row_by_entry_id[entry_id] = row



    winner_by_entry_id = {}
    df = pd.read_csv('winners.csv')
    l = len(df)

    winners_fields = "category,id,entry_id,filename,url,prize,name,email,country,facebook,instagram,website,bio".split(',')

    for i in range(l):
        winner = df.loc[i]
        entry_id = str(int(winner['entry_id']))
        winner_by_entry_id[entry_id] = winner

    entrant_by_entry_id = {}
    output = []
    df = pd.read_csv('entrants.csv')
    l = len(df)

    entrants_fields = """Timestamp
    Your Name (e.g. John Henry-Smythe, Arya Kumar, Zhang Chen)
    Where you live
    Profile
    Type of Profile Link
    Profile Link
    Your Photo ID
    Photograph Title
    Press Info""".splitlines()

    output_fields = [
        'Filename',
    'Name',
    'Award',
    'Photo ID',
    'Nationality',
    'Bio',
    'Profile Link Type',
    'Profile Link',
    'Title',
    'Caption',
    'sort',
    ]

    def replace_ids(id):

        replace = {
        '61012': '61092',
        '66250': '66283',
        }
        for k,v in replace.items():
            if id == k:
                id = v

        return id

    for i in range(l):
        entrant = df.loc[i]


        entrant_id_raw = replace_ids(str(entrant['Your Photo ID']))


        entrant_id = "".join(ch for ch in entrant_id_raw if ch.isdigit())

        if entrant_id == '':
            continue
        entrant_by_entry_id[entrant_id] = entrant

        row = row_by_entry_id[entrant_id]

        name = entrant['Your Name (e.g. John Henry-Smythe, Arya Kumar, Zhang Chen)']


        if entrant_id in winner_by_entry_id:
            winner = winner_by_entry_id[entrant_id]

            id =str(winner['id'])
            entry_id = entrant_id
            fileid = f"{id[::-1]}_{entrant_id}_{id}"


            # print(winner['category'], len(winner['category']))
            # for s in specials_index:
            #     if winner['category'].startswith(s):
            #         specials_category = winner['category']

            sort = 6
            if winner['category'] == 'Projects':
                sort = 3
                prize = replace_from_position(winner['prize'].strip())
                filename = f"PROJECTS/{prize} - {winner['name']}/{replace_from_position(winner['prize'])}-{winner['name']}-{fileid}.jpg"
            elif len(winner['category']) <= 2:
                filename = f"SPECIALS/{replace_from_specials(winner['category'])}/{replace_from_position(winner['prize'])}-{winner['name']}-{fileid}.jpg"
                sort = 5
            elif 'Year' in winner['prize']:
                filename = f"00 Photograph of the Year, Winner - Margrit Schwarz - 23656__3690__65632.jpg"
                sort = 2
            elif 'Photographer of the Year' in winner['category']:
                prize = replace_from_position(winner['prize'].strip())
                filename = f"PHOTOGRAPHER OF THE YEAR/{prize} - {winner['name']}/{replace_from_position(winner['prize']).strip().split(' ')[0]}-{winner['name']}-{fileid}.jpg"
                sort = 1
            elif 'rand' in winner['category'] or 'ntim' in winner['category'] or 'bstract' in winner['category']:
                filename = f"MAIN CATEGORIES/{replace_from_category(winner['category'])}/{replace_from_position(winner['prize'])}-{winner['name']}-{fileid}.jpg"
                sort = 4


            award = f"{replace_from_specials(replace_from_category(winner['category']))}, {winner['prize']}"

            category = winner['category']

        else:
            row = row_by_entry_id[entrant_id]
            id =str(row['id'])
            name = (row['name'])
            entry_id = entrant_id
            fileid = f"{id[::-1]}_{entrant_id}_{id}"
            category = replace_from_category(row['entry_category'])
            filename = f"EXTRAS/{name}--{category}--{fileid}.jpg"
            award = ''
            sort = 7




        output_item = {
            'sort': sort,
            'Filename': filename,
            'Name': name,
            'Award': str(award),
            'Photo ID': entrant_id,
            'Nationality': entrant['Where you live'],
            'Bio': entrant['Profile'],
            'Profile Link Type': entrant['Type of Profile Link'],
            'Profile Link':  entrant['Profile Link'],
            'Title': entrant['Photograph Title'],
            'Caption': entrant['Press Info'],
            }



        output.append(output_item)



        copy_images(id, entry_id, category, image_directory, filename, output_item, entrant, winner, row)

    pprint(output)
    output_sorted = sorted(output, key=lambda x: (x["sort"],x['Filename']))

    with open(os.path.join(target_directory, "presspack.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=output_fields)
        writer.writeheader()  # write header row
        pprint(output_sorted)
        output_clean = normalize(output_sorted)
        writer.writerows(output_clean)  # write all rows
        
    

