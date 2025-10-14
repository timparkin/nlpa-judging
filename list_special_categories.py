import pandas as pd
import requests
import os
import math
from pathlib import Path
import sys
import argparse
import yaml
import json

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--fullcsv", help="csv lookup file")
    parser.add_argument("--config", help="config file", default="config.yaml")
    args = parser.parse_args()
    config = args.config

    with open(config) as f:
         yaml_data = yaml.safe_load(f)

    yaml_args = yaml_data['args']
    fullcsv = yaml_args.get('fullcsv', args.fullcsv)

    df = pd.read_csv(fullcsv)
    l = len(df)

    tag_count = {}
    for i in range(l):
        row = df.loc[i]
        if math.isnan(row['id']):
            continue

        entry_id = int(row['entry_id'])

        id = int(row['id'])
        name = str(row['name'])
        email = str(row['email'])

        special_award_tags = json.loads(row['entry_special_award'])

        for tag in special_award_tags:
            if tag in tag_count:
                tag_count[tag] += 1
            else:
                tag_count[tag] = 1

    print(tag_count)
            
