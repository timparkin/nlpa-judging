import pandas as pd
import requests
import os
import math
from pathlib import Path
import sys
import argparse
import yaml



if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--byentryid", help="use entry ids", action='store_true')
    parser.add_argument("--fullcsv", help="csv lookup file")
    parser.add_argument("--config", help="config file", default="config.yaml")
    parser.add_argument("--ids", help="ids to lookup")
    parser.add_argument("--idsfile", help="file name for ids")
    parser.add_argument("--filenamesfile", help="file name for filenames")
    parser.add_argument("--names", help="names to lookup")
    parser.add_argument("--include", help="include the search term", action=argparse.BooleanOptionalAction, default=False)

    args = parser.parse_args()

    config = args.config
    ids = args.ids
    inc = args.include
    idsfile = args.idsfile
    filenamesfile = args.filenamesfile
    byentryid = args.byentryid

    if idsfile:
        ids = [str(int(i.strip())) for i in open(idsfile).readlines()]
    elif filenamesfile:
        filenames = [f.strip()[:-4] for f in open(filenamesfile).readlines()]
        ids = []
        for f in filenames:
            anon,id,entry_id = f.split('__')
            ids.append(entry_id)

    elif ids:
        ids = [str(int(id)) for id in ids.split(',')]
    names = args.names

    if names:
        names = [name.lower() for name in names.split(',')]


    with open(config) as f:
         yaml_data = yaml.safe_load(f)

    yaml_args = yaml_data['args']
    fullcsv = yaml_args.get('fullcsv', args.fullcsv)

    print(fullcsv)


    df = pd.read_csv(fullcsv)
    l = len(df)


    name_by_email={}
    name_by_id={}
    email_by_id={}
    website_by_id={}
    country_by_id={}
    id_by_entry_id={}
    id_by_name={}
    found = []

    for i in range(l):
        row = df.loc[i]
        if math.isnan(row['id']):
            continue

        entry_id = str(int(row['entry_id']))

        if byentryid:
            id = str(int(row['entry_id']))
        else:
            id = str(int(row['id']))
        name = str(row['name'])
        email = str(row['email'])
        website = str(row['website'])
        country = str(row['country'])

        name_by_email[email] = name
        name_by_id[id] = name
        email_by_id[id] = email
        country_by_id[id] = country
        website_by_id[id] = website
        id_by_entry_id[entry_id] = str(int(row['id']))

        if names:
            for n in names:
                if n in name.lower() and name not in found:

                    id_by_name[id] = name
                    if inc:
                        print(f"{name}: {id} ({email})")
                    else:
                        print(f"{id}, {email}")
                    found.append(name)


    if ids:
        for id in ids:
            if inc:
                print(f"{id_by_entry_id[id]},{id}: {name_by_id[id]} <{email_by_id[id]}>")
            else:
                print(f"{name_by_id[id]} <{email_by_id[id]}>. {website_by_id[id]} : {country_by_id[id]}")
