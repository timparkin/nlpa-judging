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
from urllib.parse import urlparse
from posixpath import basename, dirname


import io
from PIL import Image
from PIL import ImageCms
import sys

try:
    directory=sys.argv[1]
    source = sys.argv[2]
except:
    directory = os.getcwd()
    source = '/Volumes/X94T_2025/NLPA-2025/nlpa-2025/ORIGINALS'



base = os.path.join(directory, source)
target = os.path.join(directory,'NLPA_Round_One_Images')
print('source directory = %s'%base)
print('target directory = %s'%target)

def convert_to_srgb(img):
    '''Convert PIL image to sRGB color space (if possible)'''
    icc = img.info.get('icc_profile', '')
    if icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

# printing lowercase
letters = string.ascii_lowercase


def text_wrap(text,font,writing,max_width,max_height):
    lines = [[]]
    words = text.split(' ')
    for word in words:
        # try putting this word in last line then measure
        lines[-1].append(word)

        left, top, right, bottom = writing.multiline_textbbox((0, 0), '\n'.join([' '.join(line) for line in lines]) , font)
        (w,h) = right - left, bottom - top

        #(w,h) = writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)
        if w > max_width: # too wide
            # take it back out, put it on the next line, then measure again
            lines.append([lines[-1].pop()])

            left, top, right, bottom = writing.multiline_textbbox((0, 0), '\n'.join([' '.join(line) for line in lines]) , font)
            (w,h) = right - left, bottom - top
            #(w,h) = writing.multiline_textsize('\n'.join([' '.join(line) for line in lines]), font=font)

            if h > max_height: # too high now, cannot fit this word in, so take out - add ellipses
                lines.pop()
                # try adding ellipses to last word fitting (i.e. without a space)
                lines[-1][-1] += '...'
                # keep checking that this doesn't make the textbox too wide,
                # if so, cycle through previous words until the ellipses can fit

                left, top, right, bottom = writing.multiline_textbbox((0, 0), '\n'.join([' '.join(line) for line in lines]) , font)
                (w,h) = right - left, bottom - top

                while w > max_width:
                    lines[-1].pop()
                    lines[-1][-1] += '...'
                break
    return '\n'.join([' '.join(line) for line in lines])

title_font = ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 64)
body_font = ImageFont.truetype('assets/GrotaSansAltRd-Medium.otf', 35)



def project_text(title, description, target_filename):
    title_image = Image.open('assets/blank-black.jpg')
    writing = ImageDraw.Draw(title_image)
    description_wrapped = text_wrap(description,body_font,writing,1700,1400)
    writing.text((140,140),title,font=title_font)
    writing.text((140,250),description_wrapped,font=body_font, spacing=20)
    title_image.save(target_filename)

def resize(filename, category, directory, entry_id, id, row):
    print('%s - %s - %s'%(filename, category, directory))
    original_directory = os.path.join(base, category, directory)

    if category == "P1" or category == "P2":
        target_directory = os.path.join(target, category, id)
    else:
        target_directory = os.path.join(target, category)
    Path(target_directory).mkdir(parents=True, exist_ok=True)
    original_filename =  os.path.join(original_directory, filename)
    encoded_filename = str(entry_id)[::-1]
    anon_filename = '%s__%s__%s.jpg'%(encoded_filename,id,entry_id)
    target_filename =  os.path.join(target_directory, anon_filename)
    if not os.path.isfile(target_filename):
        image = Image.open(original_filename)
        image.thumbnail((2048, 1536))
        try:
            image_conv = convert_to_srgb(image)
        except:
            image_conv = image
        image_conv.save(target_filename, quality=80, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))



    else:
        print('** SKIPPING = %s'%target_filename)

    if category == "P1" or category == "P2":
        if category  == "P1":
            title = row['project_title_one']
            description = row['project_description_one']
        else:
            title = row['project_title_two']
            description = row['project_description_two']

        if not isinstance(title,str) and math.isnan(title):
            title = ''
        if not isinstance(description,str) and math.isnan(description):
            description = ''


        target_filename =  os.path.join(target_directory, '00_project_description.jpg')
        if not os.path.isfile(target_filename):
            project_text(title, description, target_filename)








#df = pd.read_csv('nlpa_combined_entries-final-cleaned-extra.csv')
df = pd.read_csv('nlpaentries.csv')

space = 0
for i in range(len(df)):
#for i in range(100):
    row = df.loc[i]
    print('%s of %s (%s%%)'%(i,len(df),int(100*i/len(df)) ) )
    url = row['entry_url']
    id = row['id']
    entry_id = row['entry_id']
    if not isinstance(url,str):
        if row['uploads'] == 0:
            print('no uploads')
        else:
            print('entry_id not string'%url)
        continue
    filename = str(row['entry_filename'])
    if 'entries' in filename:
        filename = filename.split('/')[-1]

    parse_object = urlparse(url)
    noclash_filename = basename(parse_object.path)

    name = row['name']
    category = row['entry_category']
    size = row['entry_photo_size']
    if not isinstance(category, str):
        print('category not string')
        category = 'undefined'

    if not math.isnan(size):
        try:
            resize(noclash_filename, category, name, str(int(entry_id)), str(int(id)), row)
        except OSError as e:
            print(e)
            print('ERROR WITH %s for %s in %s'%(noclash_filename,category,name))
    else:
        print('error with size=%s. %s for %s in %s'%(size,noclash_filename,category,name))
