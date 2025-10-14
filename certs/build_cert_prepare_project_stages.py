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
import csv
import re
import json

import yaml
from certs.build_certs import process_caption, process_secondary_caption
from final_scores import score_var_calc_judges, score_var_calc_org
from pathlib import Path



#################################################################


if __name__ == "__main__":



    import argparse
    parser = argparse.ArgumentParser()


    parser.add_argument("--config", help="yaml config file", default="config.yaml")

    args = parser.parse_args()
    config = args.config

    with open(config) as f:
         yaml_data = yaml.safe_load(f)

    yaml_args = yaml_data['args']

    projects_csv = yaml_args['projects_csv']

    full_csv = yaml_args.get('fullcsv')

    yaml_project_args = yaml_args['projectargs']

    projectsall = yaml_project_args.get('projectsall')
    secondjudging = yaml_project_args.get('secondjudging')
    showntojudges = yaml_project_args.get('showntojudges')
    secondround = yaml_project_args.get('secondround')
    semifinals = yaml_project_args.get('semifinals')

    livefinals = yaml_project_args.get('livefinals')

    project_csvs = {
    'all': pd.read_csv(projectsall,keep_default_na=False),
    'secondjudging': pd.read_csv(secondjudging,keep_default_na=False),
    'showntojudges': pd.read_csv(showntojudges,keep_default_na=False),
    'secondround': pd.read_csv(secondround,keep_default_na=False),
    'semifinals': pd.read_csv(semifinals,keep_default_na=False),
    'livefinals': pd.read_csv(livefinals,keep_default_na=False),
    }

    caption = yaml_data['caption']

    caption_sections = re.split(r'(^[A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]) ([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).*', caption, flags=re.MULTILINE)

    caption_sections = caption_sections[1:-1]

    judge_initials = []
    for n in range(8):
        judge_initials.append( caption_sections[n*2] )
    judge_initial_positions = ''.join(judge_initials[:5])






    R = {
    '* ': 1,
    '* * ': 2,
    '* * * ': 3,
    '* * * * ': 4,
    '* * * * * ': 5,
    '': 0,
    }



    def get_batch_user_id_from_path(path):


        p = Path(path).parent.name.split('-')
        if len(p) == 3:
            scratch, batch, user_id = p
        elif len(p) == 4:
            scratch, batch, user_id, scratch = p
        else:
            batch, user_id = p
        return batch, user_id


    all = {}
    showtojudges = {}
    onlyfinals = {}





    title = {}
    print('all',len(project_csvs['all']))
    for i in range(len(project_csvs['all'])):
        r = project_csvs['all'].loc[i]
        description_slide = r['File,name'] == '00_project_description.jpg'
        score = float(R[r['Rating']])
        label = r['Label']
        caption = r['Caption']
        if 'Abstract' in r['Path'] or 'Grand' in r['Path'] or 'Intimate' in r['Path']:
            continue

        batch, user_id = get_batch_user_id_from_path(r['Path'])
        filename = r['File,name']
        batch = int(batch)
        user_id = int(user_id)

        if description_slide:
            title[ (batch,user_id)] = r['Title']
        else:
            u, entry_id = [int(x) for x in r['File,name'][:-4].rsplit('__', maxsplit=2)[1:]]

            j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_secondary_caption(caption, title, judge_initial_positions)
            j_score_data = score_var_calc_judges(j_scores_list)
            o_score_data = score_var_calc_org(o_scores_list)
            if (batch,user_id) not in all:
                all[ (batch, user_id) ] = {
                    'title': title,
                    'secondjudging': False,
                    'showntojudges': False,
                    'secondround': False,
                    'semifinals': False,
                    'livefinals': False,
                    'filename': filename,
                    'j_scores': json.dumps(j_scores),
                    'o_scores': json.dumps(o_scores),
                    'j_score_data': json.dumps(j_score_data),
                    'o_score_data': json.dumps(o_score_data),
                    'path': Path(r['Path']).parent.name,
                }

    # Set the title for every image that isn't a project description
    for key in all.keys():
        all[key]['title'] = title[key]



    print('secondjudging',len(project_csvs['secondjudging']))

    for i in range(len(project_csvs['secondjudging'])):
        r = project_csvs['secondjudging'].loc[i]
        description_slide = r['File,name'] == '00_project_description.jpg'
        batch, user_id = get_batch_user_id_from_path(r['Path'])
        caption = r['Caption']
        title = r['Title']

        if batch == 'Jan':
            batch = 1
        if batch == 'Feb':
            batch = 2
        batch = int(batch)
        user_id = int(user_id)

        all[ (batch,user_id) ]['secondjudging'] = True








    print('showntojudges',len(project_csvs['showntojudges']))

    for i in range(len(project_csvs['showntojudges'])):
        r = project_csvs['showntojudges'].loc[i]
        description_slide = r['File,name'] == '00_project_description.jpg'
        batch, user_id = get_batch_user_id_from_path(r['Path'])
        caption = r['Caption']
        title = r['Title']
        if batch == 'Jan':
            batch = 1
        if batch == 'Feb':
            batch = 2



        batch = int(batch)
        user_id = int(user_id)
        all[ (batch,user_id) ]['showntojudges'] = True

        if description_slide:
            continue
        # print('#'*20)
        # print(caption)
        j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_caption(caption, title, judge_initial_positions)
        # print(j_scores)
        # print(j_score_data)

        j_score_data = score_var_calc_judges(j_scores_list)

        all[ (batch,user_id) ]['j_scores'] = json.dumps(j_scores)
        all[ (batch,user_id) ]['j_score_data'] = json.dumps(j_score_data)



    print('secondround',len(project_csvs['secondround']))

    for i in range(len(project_csvs['secondround'])):
        r = project_csvs['secondround'].loc[i]
        batch, user_id = get_batch_user_id_from_path(r['Path'])

        batch = int(batch)
        user_id = int(user_id)
        all[ (batch,user_id) ]['secondround'] = True

    print('semifinals',len(project_csvs['semifinals']))

    for i in range(len(project_csvs['semifinals'])):
        r = project_csvs['semifinals'].loc[i]
        batch, user_id = get_batch_user_id_from_path(r['Path'])

        if batch == 'Jan':
            batch = 1
        if batch == 'Feb':
            batch = 2
        batch = int(batch)
        user_id = int(user_id)
        all[ (batch,user_id) ]['semifinals'] = True

    print('livefinals',len(project_csvs['livefinals']))

    for i in range(len(project_csvs['livefinals'])):
        r = project_csvs['livefinals'].loc[i]

        batch, user_id = get_batch_user_id_from_path(r['Path'])

        if batch == 'Jan':
            batch = 1
        if batch == 'Feb':
            batch = 2
        batch = int(batch)
        user_id = int(user_id)
        all[ (batch,user_id) ]['livefinals'] = True



    c = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
    }

    ca = {
        1: 0,
        2: 0,
        3: 0,
        4: 0,
        5: 0,
        6: 0,
    }

    with open(projects_csv, mode='w') as p:
        writer = csv.writer(p, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            'batch',
            'user_id',
            'secondjudging',
            'showntojudges',
            'secondround',
            'semifinals',
            'livefinals',
            'filename',
            'title',
            'j_scores',
            'o_scores',
            'j_score_data',
            'o_score_data',
            'path',
    ])

        for key, C in all.items():

            batch, user_id = key
            writer.writerow([
            batch,
            user_id,
            C.get('secondjudging'),
            C.get('showntojudges'),
            C.get('secondround'),
            C.get('semifinals'),
            C.get('livefinals'),
            C.get('filename'),
            C.get('title'),
            C.get('j_scores'),
            C.get('o_scores'),
            C.get('j_score_data'),
            C.get('o_score_data'),
            C.get('path'),
            ])


            if C.get('livefinals'):
                c[6] += 1
            elif C.get('semifinals'):
                c[5] += 1
            elif C.get('secondround'):
                c[4] += 1
            elif C.get('showntojudges'):
                c[3] += 1
            elif C.get('secondjudging'):
                c[2] += 1
            else:
                c[1] += 1


            if C.get('livefinals'):
                ca[6] += 1
            if C.get('semifinals'):
                ca[5] += 1
            if C.get('secondround'):
                ca[4] += 1
            if C.get('showntojudges'):
                ca[3] += 1
            if C.get('secondjudging'):
                ca[2] += 1

        print(c)

        print(ca)


