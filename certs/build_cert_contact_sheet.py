import glob
from PIL import Image
import yaml
import pandas as pd
import math
import sys

def make_contact_sheet(fnames,ncols,nrows,photow,photoh, marl,mart,marr,marb, padding):
    """\
    Make a contact sheet from a group of filenames:

    fnames       A list of names of the image files

    ncols        Number of columns in the contact sheet
    nrows        Number of rows in the contact sheet
    photow       The width of the photo thumbs in pixels
    photoh       The height of the photo thumbs in pixels

    marl         The left margin in pixels
    mart         The top margin in pixels
    marr         The right margin in pixels
    marl         The left margin in pixels

    padding      The padding between images in pixels

    returns a PIL image object.
    """
    # Read in all images and resize appropriately
    imgs = [Image.open(fn).resize((photow,photoh), Image.LANCZOS) for fn in fnames]



    if len(imgs)%2 == 1:
        middle = True
    else:
        middle = False
    # Calculate the size of the output image, based on the
    #  photo thumb sizes, margins, and padding
    marw = marl+marr
    marh = mart+ marb

    padw = (ncols-1)*padding
    padh = (nrows-1)*padding
    isize = (ncols*photow+marw+padw,nrows*photoh+marh+padh)



    # Create the new image. The background doesn't have to be white
    white = (255,255,255)
    inew = Image.new('RGB',isize,white)

    # Insert each thumb:
    for irow in range(nrows):
        for icol in range(ncols):
            left = marl + icol*(photow+padding)
            right = left + photow
            upper = mart + irow*(photoh+padding)
            lower = upper + photoh
            try:
                img = imgs.pop(0)
            except:
                break
            if irow+1 == nrows and middle:
                left = marl + (photow+padding)//2
                right = left + photow
            bbox = (left,upper,right,lower)

            inew.paste(img,bbox)
    return inew

from math import ceil
import os




config = 'config.yaml'
with open(config) as f:
     yaml_data = yaml.safe_load(f)

yaml_args = yaml_data['args']

cert_folder = yaml_args['cert_folder']
certs_csv = yaml_args['certs_csv']
full_csv = yaml_args['fullcsv']
special_winners = yaml_data['special_winners']
cat_winners = yaml_data['cat_winners']
projects = yaml_data['projects']
poty = yaml_data['poty']



winners = []

# for k,v in special_winners.items():
#     for l, w in v.items():
#         winners.append(l)
#
# for k,v in cat_winners.items():
#     for l, w in v.items():
#         winners.append(l)
#
# for k,v in projects.items():
#     winners.append(k)
#
# for k,v in poty.items():
#     winners.append(k)



for k, v in cat_winners.items():

    for K, V in v.items():
        winners.append( K )









for k, v in special_winners.items():
    for K,V in v.items():
        winners.append(K)

for k in projects:
    winners.append(k.split('-')[1])

for k in poty:
    winners.append(k)



df = pd.read_csv(full_csv)
entry_by_user_id = {}
for i in range(len(df)):
    r = df.loc[i]
    id = r['id']
    if math.isnan(id):
        continue
    entry_id = r['entry_id']
    if id in entry_by_user_id:
        entry_by_user_id[id].append(r)
    else:
        entry_by_user_id[id] = [r]




df = pd.read_csv(certs_csv)


certs_by_id = {}

# this is to skip onees alreeaedy sent. id's are produced by the code as general output
# Might be worth storing ID's in a file instead
exclusions = []

for i in range(len(df)):

    r = df.loc[i]
    user_id = r['id']
    if user_id in exclusions:
        continue
    target_filename = r['target_filename']
    name = r['name']
    email = entry_by_user_id[user_id][0]['email']
    subheader = r['subheader']
    stage_text = r['stage_text']
    prize = r['prize']
    ttype = r['type']

    if isinstance(subheader, float):
        subheader = ttype.title()
    data = {
        'email': email,
        'user_id': user_id,
        'target_filename': target_filename,
        'name': name,
        'subheader': subheader,
        'stage_text': stage_text,
        'prize': prize,
        'type': ttype,
    }
    if user_id not in certs_by_id:
        certs_by_id[user_id] = [ data ]
    else:
        certs_by_id[user_id].append( data )



build_hires = True




for user_id, certs in certs_by_id.items():


    photow,photoh = 300,300



    cert_items = []
    max_stage = 0

    highest_stage = 0
    for cert in certs:
        stage_text = cert['stage_text']
        type = cert['type']
        if type == 'project':
            stage_max = 5
        else:
            stage_max = 6
        stage_number = int(stage_text[0])
        stage_name = stage_text[2:].split('(')[0].strip()
        subheader = cert['subheader']
        category = subheader.split(',')[0]

        if ',' in subheader:
            award = subheader.split(',')[1].strip()
            prize = ' ({})'.format(award)
        else:
            award = None
            prize = ''
        if award =="Winner":
            stage_number = 12
        elif award == "Runner Up":
            stage_number = 11
        elif award == "Third Place":
            stage_number = 10
        elif award == "Fourth Place":
            stage_number = 9
        elif award == "Fifth Place":
            stage_number = 8
        elif award == "Highly Commended":
            stage_number = 7


        if type == "project":
            category = f'Project: "{category}"'

        max_stage = max(stage_number, max_stage)
        if stage_number > 6:
                cert_text = f'{category}, {award}'
        else:
            cert_text = f'{category} (stage {stage_number} out of {stage_max}, {stage_name})'

        highest_stage = max(highest_stage, stage_number)
        cert_items.append( (stage_number/stage_max, cert['target_filename'] ) )

    cert_items.sort(key=lambda tup: tup[0], reverse=True)

    print(user_id)
    if (int(user_id)==1912):

        print(cert_items)




    files = [i[1] for i in cert_items]





    if len(files) == 0:
        continue
    f = []
    ncols = 2
    nrows = ceil(len(files)/2)




    photo = (photow,photoh)

    margins = [0,0,0,0]

    padding = 0




    inew = make_contact_sheet(files,ncols,nrows,*photo,*margins,padding)
    inew.save('{}/{}/contacts.jpg'.format(cert_folder,str(user_id)), quality=93)
    #os.system('display bs.png')
