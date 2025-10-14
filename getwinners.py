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
import io
from PIL import Image
from PIL import ImageCms
import sys
import shutil
import json
from imgtag import ImgTag
import traceback
import copy
import datetime
from urllib.parse import urlparse, unquote
from posixpath import basename, dirname

MAKE_ANONYMOUS = False

def saveimage(row, base,newname, directory, entry_id = None):
    anon_filename = '%s__%s.jpg' % (row['id'], row['entry_id'])

    url = 'https://submit.naturallandscapeawards.com/%s' % row['entry_url']
    filename = str(row['entry_filename'])
    if 'entries' in filename:
        filename = filename.split('/')[-1]
    parse_object = urlparse(url)
    noclash_filename = basename(parse_object.path)



    category = str(row['entry_category'])


    if directory.startswith('P'):
        original_directory = os.path.join(base, directory)
    else:
        original_directory = os.path.join(base,directory,row['name'])
    # ORIGINAL NAME ISN"T PICKING UP THE CORRECT NO CLASH VERSION
    original_filename = os.path.join(original_directory, noclash_filename)
    out_directory = os.path.join('/Users/timparkin/nlpa-2025', 'winners-2048')
    if not os.path.exists(out_directory):
        os.mkdir(out_directory)

    if os.path.exists(original_filename):
        image = Image.open(original_filename)
    else:
        for d in ['GS','IL','AD','P1','P2']:
            original_directory = os.path.join(base, d, row['name'])
            original_filename = os.path.join(original_directory, noclash_filename)
            if os.path.exists(original_filename):
                image = Image.open(original_filename)
                break



    if entry_id is not None:
        if not os.path.exists(os.path.join(out_directory, newname)):
            os.mkdir(os.path.join(out_directory, newname))
        anon_out = os.path.join(out_directory, newname, '%s_%s.jpg'%(newname,entry_id))
    else:
        if "Photograph of the Year" in newname:
            newname = newname.split('_',1)[1]
        anon_out = os.path.join(out_directory, '%s.jpg'%newname)
    # **** RESIZE THIS IMAGE

    image.thumbnail((2048, 2048))
    # image.thumbnail((1024,768))

    # Convert to sRGB (possible errors making things green in places in some images?)
    try:
        image_conv = convert_to_srgb(image)
    except:
        image_conv = image
    # ***** SAVE THE IMAGE AND SET COMPRESSION
    image_conv.save(anon_out, quality=92, format="JPEG", icc_profile=image_conv.info.get('icc_profile', ''))
    image.close()

missing_ids = [int(n) for n in """999
""".splitlines()]

def shifttext(text, shift):
    a = ord('a')
    return ''.join(chr((ord(char) - a + int(shift)) % 26 + a) for char in text.lower())

skip_project = []
project_min_score = 18

# THESE ARE EXTRA IMAGES THAT DIDN"T SCORE A ONE STAR BUT I WANT TO INCLUDE
# include these images
extras_ids = []
# include these projects [(c,id),]
project_extras = []
# Only include these ids if not none [(c,id),]
finals_project_filter = None

skip_portfolio = []
portfolio_min_score = 18

# THIS CODE IS ODD AS I COPIED THE FILES FROM THE ORIGINAL CACHE, THEN DOWNLOADED THE RAW FILES, ONLY TO REALISE I HADN'T REASSIGNED THE CATEGORIES.
# THE NEW_TARGET IS A DUPLICATE FOLDER WITH REMAPPED CATEGORIES - QUITE HANDY IN THE END AS I COULD WIPE IT AND THE RECREATION PROCESS WASN'T THAT EXPENSIVE.
# FOR THE NEXT RUN I NEED TO MAKE SURE I REMAP THE CATEGORIES FORST - TO FOR THE NEXT YEAR

#
# target_directory = where to pout downloads
# anon_prefix = filename prefix to randomise sorting
# directory = NOT used

def save_raw_from_url(cache_directory, target_directory, new_target_directory, anon_prefix, url, filename, category, directory, id, rating, label, title, description, city, name, rawchecking):
    if rawchecking != 'Grey':
        print(rawchecking)

    ftp_folder="/mnt2/nlpa/raws"

    Path(target_directory).mkdir(parents=True, exist_ok=True)
    Path(new_target_directory).mkdir(parents=True, exist_ok=True)


    ftp_filename = os.path.join(ftp_folder, filename)

    raw_name, raw_suffix = os.path.splitext(filename)

    raw_filename = ''.join((raw_name, '-RAW', raw_suffix))
    xmp_filename = ''.join((raw_name, '-RAW', '.xmp'))
    new_target_filename =  os.path.join(new_target_directory, '%s_%s'%(anon_prefix,raw_filename))
    new_xmp_filename = os.path.join(new_target_directory, '%s_%s'%(anon_prefix,xmp_filename))

    # THIS NEEDS TO SAVE TO A CACHE FOR ATOMIC COPIES
    # MAKE target_filename = cache_filename

    if not os.path.isfile(new_target_filename):
        print('getting original raw - %s'%filename)
        try:
            shutil.copy2(ftp_filename,new_target_filename)
        except (FileNotFoundError, OSError) as e:
            print(f'Error copying file: {e}')
            print(ftp_filename, os.path.exists(ftp_filename))
            shutil.copy2(unquote(ftp_filename),new_target_filename)

    xmp_content = xmp.format(rating=rating, filename=raw_filename, label=rawchecking, title=title, description=description, city=city, flag=rawchecking)
    with open(new_xmp_filename, "w") as text_file:
        text_file.write(xmp_content)

    if raw_suffix == 'jpg':
        data = {
            'Rating': rating,
            'Label': rawchecking,
            'Title': title,
            'Description': description,
            'Rights': '',
            'Creator': name,
            'City': city,
            'State': '',
            'Country': '',

        }
        write_xmp(new_target_filename, data)

# oragniser scores
def score_var_calc_org(scoresx):

    scores = [scoresx[0], scoresx[1], scoresx[2], scoresx[3], scoresx[4]]

    # sort scores to low first
    scores.sort()

    # count all reject scores
    rejects = scores.count(2)+scores.count(1)+scores.count(0)
    # count high scorees (4s)
    highs = scores.count(4)
    # count highest (5s)
    tops = scores.count(5)

    # var is the variance score
    var = 0



    # make the score the average of evereything skipping the lowest score
    score = S.mean(scores)
    mean = score
    raw_score = score

    if tops >= 2:
        score = 5.0

    elif tops >= 1:
        score = 4.666

    elif highs >= 2:
        score = 4.333

    elif highs >= 1:
        score = 4.0

    tscore = score




    if raw_score*3 == 11.0:
        var = 1
    if raw_score*3 == 12.0:
        var = 2
    if raw_score*3 == 13.0:
        var = 3
    if raw_score*3 == 14.0:
        var = 4
    if raw_score*3 >= 15.0:
        var = 5



    score_data = {
        'score': score,
        'raw_mean': raw_score,
        'mean': mean,
        'variance': S.variance(scoresx),
        'label': int(var),
        'scores': [int(s) for s in scoresx],
    }
    return score_data

# Judges scores
def score_var_calc(arg_scores):

    arg_mean = (S.mean(arg_scores)+3.0)*10/7
    variance = S.pvariance(arg_scores)
    score_data = {
        'mean': arg_mean,
        'raw_mean': S.mean(arg_scores),
        'mean_all': S.mean(),
        'variance': variance,
        'label': None,
        'scores': [int(s) for s in arg_scores],
    }

    return score_data


def score_var_calc_judges(scores_list):


    scores = copy.deepcopy(scores_list)

    raw_scores = scores
    scores.sort()
    # get rid of lowest two scores
    scores_skiplow = scores[2:]
    # count all reject scores
    rejects = scores.count(2)+scores.count(1)
    # count high scorees (4s)
    highs = scores.count(4)
    # count highest (5s)
    tops = scores.count(5)

    # var is the variance score
    var = 0

    # make the score the average of evereything skipping the lowest score
    score = S.mean(scores_skiplow)
    score_mean = S.mean(scores)
    raw_score = score

    if tops >= 3:
        if highs >=1:
            score = 5
        else:
            score = 4
    elif tops == 2:
        score = 3
    elif tops == 1:
        score = 2
    elif score_mean >= 3.2:
        score = 1
    else:
        score = 0



    score_data = {
        'score': score,
        'raw_mean': raw_score,
        'mean_all': score_mean,
        'variance': S.variance(raw_scores),
        'label': var,
        'scores': [int(s) for s in scores_list],
    }

    return score_data

# Convert imag to sRGB given PIL image as argumnt
def convert_to_srgb(img):
    '''Convert PIL image to sRGB color space (if possible)'''
    icc = img.info.get('icc_profile', '')
    if icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    return img

# Write XMP code
def write_xmp(path, data):
    if not MAKE_ANONYMOUS:
        try:
            metadata = pyexiv2.ImageMetadata(path)
            metadata.read()
            metadata['Xmp.xmp.Label'] = str(data.get('Label',''))
            metadata['Xmp.xmp.Rating'] = int(data.get('Rating',0))
            metadata['Xmp.dc.title'] = data.get('Title','')
            metadata['Xmp.dc.description'] = data.get('Description','')
            metadata['Xmp.dc.creator'] = [data.get('Creator','')]
            metadata['Xmp.dc.rights'] = data.get('Creator','')
            metadata['Exif.Image.DateTime'] = datetime.datetime(2025, 6, 21, 0, 0, 0) - datetime.timedelta(0,round((data.get('State',2.4)-2.4)*2.083,3)*1000)
            metadata['Iptc.Application2.City'] = [str(data.get('City',0))]
            metadata['Iptc.Application2.ProvinceState'] = [str(data.get('State',0))]
            metadata['Iptc.Application2.CountryName'] = [str(data.get('Country',0))]
            metadata.write()
        except RuntimeError:
            print(f'xmp runtime error {path}')

    else:
        try:
            metadata = pyexiv2.ImageMetadata(path)
            metadata.read()
            if data.get('State',2.4) >= 4:
                metadata['Xmp.xmp.Label'] = 'Green'
            else:
                metadata['Xmp.xmp.Label'] = ''
            metadata['Xmp.dc.title'] = ''  # str(data.get('State',2.4)) + ' -- ' + str(round((data.get('State',2.4)-2.4)*2.083,3)) + ' -- ' + str(data.get('City', '')) # ''
            metadata['Xmp.dc.description'] = ''
            metadata['Xmp.dc.creator'] = ['']
            metadata['Xmp.dc.rights'] = ''
            metadata['Exif.Image.DateTime'] = datetime.datetime(2025, 6, 21, 0, 0, 0) - datetime.timedelta(0,round((data.get('State',2.4)-2.4)*2.083,3)*1000)
            metadata['Xmp.xmp.Rating'] = 0 # int( round((data.get('State',2.4)-2.4)*2.083))
            metadata['Iptc.Application2.City'] = [str(data.get('City',0))]
            metadata['Iptc.Application2.ProvinceState'] = [str(data.get('State',0))]
            metadata['Iptc.Application2.CountryName'] = [str(data.get('Country',0))]
            metadata.write()
        except RuntimeError:
            print(f'xmp runtime error {path}')
    return


#def write_xmp(path, data):
#    try:
#        I = pyexiv2.Image(path)
#        I.modify_xmp({'Xmp.xmp.Label': data.get('Label','')})
#        I.modify_xmp({'Xmp.xmp.Rating': str(data.get('Rating',0))})
#        I.modify_xmp({'Xmp.dc.title': {'lang="x-default"': data.get('Title','')}})
#        I.modify_xmp({'Xmp.dc.description': {'lang="x-default"': data.get('Description','')}})
#        I.modify_xmp({'Xmp.dc.creator': data.get('Creator','')})
#        I.modify_xmp({'Xmp.dc.rights': {'lang="x-default"': data.get('Creator','')}})
#        I.close()
#    except RuntimeError:
#        pass
#        #print(path)
#    return

# Library for text wrapping basd on text, font and height etc
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

# Quick code to create the project text as an image
def project_text(title, description, target_filename):
    title_image = Image.open('assets/blank-black.jpg')
    writing = ImageDraw.Draw(title_image)
    description_wrapped = text_wrap(description,body_font,writing,1700,1400)
    writing.text((140,140),title,font=title_font)
    writing.text((140,250),description_wrapped,font=body_font, spacing=20)
    title_image.save(target_filename)

# The main loop to xtract and resize the image
def resize(filename,
            category,
            directory,
            entry_id,
            id,
            row,
            judge_project_score_lookup,
            judge_entry_score_lookup,
            organiser_project_adjust_lookup,
            organiser_entry_adjust_lookup,
            organiser_project_adjust_label_lookup,
            organiser_entry_adjust_label_lookup,
            extras_in_finals,
            extra_lookup,
            organiser_entry_score_lookup,
            organiser_entry_label_lookup,
            organiser_project_score_lookup,
            name,
            country,
            in_second_round,
            entry_rawchecking_lookup,
            project_rawchecking_lookup,
            minscore,
            target_base,
            new_target,
            for_judge,
            anon,
            comparison,
           ):


    if entry_id in missing_ids:
        print('missing check 1 {}'.format(entry_id))

    if category == 'undefined':
        print('undefined')
        print(entry_id,filename)
        return None, None


    original_directory = os.path.join(base, category, directory)

    try:
        judge_entry_scores = {
            'R': judge_entry_score_lookup.get( (id, entry_id, 'R'), 0),
            'L': judge_entry_score_lookup.get( (id, entry_id, 'L'), 0),
            'M': judge_entry_score_lookup.get( (id, entry_id, 'M'), 0),
            'P': judge_entry_score_lookup.get( (id, entry_id, 'P'), 0),
            'H': judge_entry_score_lookup.get( (id, entry_id, 'H'), 0),

        }



        judge_scores_list = [
            judge_entry_scores['R'],
            judge_entry_scores['L'],
            judge_entry_scores['M'],
            judge_entry_scores['P'],
            judge_entry_scores['H'],

            ]

        #### GET MAIN JUDGE SCORES ####
        judge_scores = score_var_calc_judges(judge_scores_list)

        # score_data = {
        #     'score': score,
        #     'raw_mean_skiplow': raw_score,
        #     'mean_all': score_mean,
        #     'variance': S.variance(raw_scores),
        #     'label': var,
        #     'scores': [int(s) for s in scores_list],
        # }

        score = judge_scores['score']
        mean = judge_scores['mean_all']
        raw_score = judge_scores['raw_mean']
        variance = judge_scores['variance']



        organiser_scores = {
            'N': organiser_entry_score_lookup.get((id, entry_id, 'N'), 2),
            'Y': organiser_entry_score_lookup.get((id, entry_id, 'Y'), 2),
            'T': organiser_entry_score_lookup.get((id, entry_id, 'T'), 2),
            'R': organiser_entry_score_lookup.get((id, entry_id, 'R'), 2),
            'M': organiser_entry_score_lookup.get((id, entry_id, 'M'), 2),

        }

        organiser_labels = {
            'N': project_label_lookup.get((id, entry_id, 'N'), 2),
            'Y': project_label_lookup.get((id, entry_id, 'Y'), 2),
            'T': project_label_lookup.get((id, entry_id, 'T'), 2),
            'R': project_label_lookup.get((id, entry_id, 'R'), 2),
            'M': project_label_lookup.get((id, entry_id, 'M'), 2),
        }

        # scores_list is judge scores
        # organiser_scores, organiser_labels <-- obvious



        raw_adjust_label = 'Grey'
        project_adjust_label = 'Grey'
        # Get the organiser scores
        entry_adjust_label = []
        try:

            if category == "P1" or category == "P2":
                project_scores_org = {
                    'N': organiser_project_score_lookup.get( (id, entry_id, 'N'), 2),
                    'Y': organiser_project_score_lookup.get( (id, entry_id, 'Y'), 2),
                    'T': organiser_project_score_lookup.get( (id, entry_id, 'T'), 2),
                    'R': organiser_project_score_lookup.get( (id, entry_id, 'R'), 2),
                    'M': organiser_project_score_lookup.get( (id, entry_id, 'M'), 2),
                }
                scores_list = [project_scores_org['N'],project_scores_org['Y'],project_scores_org['T'],project_scores_org['R'],project_scores_org['M']]


                #### GET ORGANISER SCORES (PROJECTS) ####
                org_scores = score_var_calc_org(scores_list)
                raw_score_org = org_scores['raw_mean']
                mean_score_org = org_scores['score']
                mean_mean_org = org_scores['mean']
                variance_org = org_scores['variance']
                if category == "P1":
                    c = 1
                if category == "P2":
                    c = 2


                if int(organiser_project_adjust_lookup.get((id, entry_id, 'T'), 0)) == -1:
                    mean_score_org = float(4)


                if int(organiser_project_adjust_lookup.get((id, entry_id, 'T'), 0)) == 1:
                    mean_score_org = float(5)


                if finals_project_filter and (c,int(id)) not in finals_project_filter:
                    print('project filter')
                    print(entry_id,filename)
                    return None, None




                rawchecking = project_rawchecking_lookup.get( (id, category[1]), 'Grey' )

            else:
                entry_scores_org = {
                    'N': organiser_entry_score_lookup.get( (id, entry_id, 'N'), 2),
                    'Y': organiser_entry_score_lookup.get( (id, entry_id, 'Y'), 2),
                    'T': organiser_entry_score_lookup.get( (id, entry_id, 'T'), 2),
                    'R': organiser_entry_score_lookup.get( (id, entry_id, 'R'), 2),
                    'M': organiser_entry_score_lookup.get( (id, entry_id, 'M'), 2),

                }
                scores_list = [entry_scores_org['N'],entry_scores_org['Y'],entry_scores_org['T'],entry_scores_org['R'],entry_scores_org['M']]

                #### GET ORGANISER SCORES (ENTRIES) ####
                org_scores = score_var_calc_org(scores_list)
                raw_score_org = org_scores['raw_mean']
                mean_score_org = org_scores['mean']
                variance_org = org_scores['variance']

                first_round = False
                for s in scores_list:
                    if s>=3:
                        first_round = True

                entry_adjust_label = organiser_entry_adjust_label_lookup.get( (id, entry_id) )

                rawchecking = entry_rawchecking_lookup.get( (id, entry_id), 'Grey' )
        except KeyError as e:
            print('keyerror',e)
            return None, None



    except KeyError as e:
        print('keyerror',e)
        return None, None


    # At this point all we've done is work out the scores
    # We could return at this point to compile the portfolio.py
    #return mean_score, raw_score, svar


    extra_judge = ''
    # This part target directory for prjects as opposed to entries.
    # It puts anything 3 or less into the secondary, 'optional' folder (for the finals calculation)
    #

    if category == "P1" or category == "P2":
        new_category = category
        cache_directory = os.path.join(target_base, 'cache', category_lookup[category])
    else:
        new_category = category
        if entry_adjust_label is not None:
            if entry_adjust_label.get('T') == 'green' or entry_adjust_label.get('N') == 'green' or entry_adjust_label.get('Y') == 'green' or entry_adjust_label.get('M')  == 'green':
                new_category = 'GS'
            if entry_adjust_label.get('T') == 'yellow' or entry_adjust_label.get('N') == 'yellow' or entry_adjust_label.get('Y') == 'yellow' or entry_adjust_label.get('M')  == 'yellow':
                new_category = 'IL'
            if entry_adjust_label.get('T') == 'red' or entry_adjust_label.get('N') == 'red' or entry_adjust_label.get('Y') == 'red' or entry_adjust_label.get('M')  == 'red':
                new_category = 'AD'

            # tim's categories trump
            if entry_adjust_label.get('T') == 'green' or entry_adjust_label.get('final') == 'green':
                new_category = 'GS'
            if entry_adjust_label.get('T') == 'yellow' or entry_adjust_label.get('final') == 'yellow':
                new_category = 'IL'
            if entry_adjust_label.get('T') == 'red' or entry_adjust_label.get('final') == 'red':
                new_category = 'AD'

        cache_directory = os.path.join(target_base, 'cache', category_lookup[new_category])



    category_placement = category_lookup[new_category]

    # WHY HAVE WE GOT A BASE TARGET AND A NEW TARGET?

    if category == "P1" or category == "P2":
        target_directory = os.path.join(target_base, category_lookup[new_category], '{:0>1.1f}-{}-{}'.format((raw_score*5 + raw_score_org*4)/9,new_category[1],id))
        new_target_directory = os.path.join(new_target, category_lookup[new_category], '{:0>1.1f}-{}-{}'.format((raw_score*5 + raw_score_org*4)/9,new_category[1],id))
        if int(score) < minscore and (int(category[1]),int(id)) not in project_extras:
            return None, None
    else:
        if int(entry_id) not in extras_in_finals:
            target_directory = os.path.join(target_base, category_lookup[new_category])
            new_target_directory = os.path.join(new_target, category_lookup[new_category])
        else:
            target_directory = os.path.join(target_base, secondary, category_lookup[new_category])
            new_target_directory = os.path.join(new_target, secondary, category_lookup[new_category])

        if int(score) < minscore and int(entry_id) not in extras_ids:
            return None, None

    # catch issues with mounts
    mount_root = Path(new_target_directory).anchor
    if not Path(mount_root).exists():
        raise RuntimeError(f"Mount point {mount_root} does not exist.")

    # make sure our directory exists
    Path(target_directory).mkdir(parents=True, exist_ok=True)
    Path(new_target_directory).mkdir(parents=True, exist_ok=True)
    Path(cache_directory).mkdir(parents=True, exist_ok=True)


    # Get the original filename
    original_filename =  os.path.join(original_directory, filename)
    # encode the filename THIS NEEDS WORK AS IT ISN"T RANDOM ENOUGH

    encoded_filename = str(entry_id)[::-1]
    anon_filename = '%s__%s__%s.jpg'%(encoded_filename,id,entry_id)
    anon_prefix = '%s__%s__%s'%(encoded_filename,id,entry_id)

    # Use the anon_filename to create the target
    target_filename =  os.path.join(target_directory, anon_filename)
    new_target_filename = os.path.join(new_target_directory, anon_filename)
    cache_filename = os.path.join(cache_directory, anon_filename)

    # score = judge_scores['score']
    # mean = judge_scores['mean_all']
    # raw_score = judge_scores['raw_mean']
    # variance = judge_scores['variance']


    title=''
    d = ''
    if for_judge and anon:
        title = "{}: {:.0f} | combined: {:.1f}".format(for_judge, judge_entry_scores[for_judge], raw_score)
        d += "R{R:.0f} L{L:.0f} M{M:.0f} P{P:.0f} H{H:.0f} ".format(**judge_entry_scores)
        if rawchecking == 'Red':
            return None, None

    if not anon:

        if not comparison:
            title = 's{:.0f} m{:0>1.2f} r{:0>1.2f} v{:0>1.2f}'.format(score, mean, raw_score, variance)
            d += "R{R:.0f}.L{L:.0f}.M{M:.0f}.P{P:.0f}.H{H:.0f} ".format(**judge_entry_scores)
            d += "N{N:.0f}.Y{Y:.0f}.T{T:.0f}.A{M:.0f}.J{R:.0f}".format(**organiser_scores)
            d += '\ncountry={}'.format(country)
        else:
            title = 's{:.0f} m{:0>1.2f} r{:0>1.2f} v{:0>1.2f} vo{:0>1.2f}'.format(score, mean, raw_score, variance, variance_org)
            d += "R{R:.0f}.L{L:.0f}.M{M:.0f}.P{P:.0f}.H{H:.0f} ".format(**judge_entry_scores)
            d += "N{N:.0f}.Y{Y:.0f}.T{T:.0f}.A{M:.0f}.J{R:.0f}".format(**organiser_scores)
            d += '\ncountry={}'.format(country)


    description = d


    if for_judge:

        # This is the label colour score
        label = ''
        rating = judge_entry_scores[for_judge]
        city = round(raw_score, 2)
        state = round(org_scores['mean'], 2)
        country = str(score) + '_' + str(round(mean, 2))
    else:
        if not comparison:
            label = rawchecking
            rating = int(score)
            city = round(raw_score, 2)
            state = round(org_scores['mean'], 2)
            country = str(score) + '_' + str(round(mean, 2))
        else:
            label = rawchecking
            rating = int(score)
            city = round(raw_score, 2)
            state = round(org_scores['mean'], 2)
            country = str(score) + '_' + str(round(mean, 2))



    special_award_tags = json.loads(row['entry_special_award'])



    if get_raws and in_second_round:

        # EXTRA CODE TO COPY RAW FILES!!!
        eu1 = row['evidence_url_1']
        eu2 = row['evidence_url_2']
        eu3 = row['evidence_url_3']
        eu4 = row['evidence_url_4']
        eu5 = row['evidence_url_5']

        allfiles = []
        for f in [eu1,eu2,eu3,eu4,eu5]:
            try:
                isnan = math.isnan(f)
                continue
            except Exception as e:
                allfiles.append(f)


        efiles = [f for f in allfiles if f != '' and not f.endswith('default-entry.png')]
        for f in efiles:
            save_raw_from_url(cache_directory, target_directory, new_target_directory, anon_prefix, 'https://submit.naturallandscapeawards.com%s'%f, f.split('/')[-1], category, directory, id, rating, label, title, description, city, name, rawchecking)



    # Check to see if we've already processed this image
    if not dryrun and in_second_round:
        if not os.path.isfile(target_filename):


            image = Image.open(original_filename)
            # **** RESIZE THIS IMAGE
            image.thumbnail((4000,4000))
            #image.thumbnail((1024,768))

            # Convert to sRGB (possible errors making things green in places in some images?)
            try:
                image_conv = convert_to_srgb(image)
            except:
                image_conv = image
            # ***** SAVE THE IMAGE AND SET COMPRESSION
            if not dryrun:
                image_conv.save(target_filename, quality=92, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))

            #image_conv.save(target_filename, quality=70, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))
            image.close()

            # This is the proper data stored for Lightroom. I've added our scores in the description here
            if not anon:
                data = {
                    'Rating': rating,
                    'Label': label,
                    'Title': title,
                    'Description': description,
                    'Rights': country,
                    'Creator': name,
                    'City': city,
                    'State': state,
                    'Country': country,

                }
            else:
                data = {
                    'Label': label,
                    'Rating': rating,
                    'Description': description,
                    'Title': title,
                    'City': city,
                    'State': state,
                    'Country': country,
                    'Creator': '',
                }
            if not dryrun:
                write_xmp(target_filename, data)
        else:

            # If we have already processed this image, refresh the metadata as we could be trying to rescore things
            if not anon:
                data = {
                    'Rating': rating,
                    'Label': label,
                    'Title': title,
                    'Description': description,
                    'Rights': country,
                    'Creator': name,
                    'City': city,
                    'State': state,
                    'Country': country,
                }
            else:
                data = {
                    'Label': label,
                    'Rating': rating,
                    'Description': description,
                    'Title': title,
                    'City': city,
                    'State': state,
                    'Country': country,
                    'Creator': '',
                }

        if not os.path.isfile(new_target_filename):
            shutil.copy2(target_filename, new_target_filename)
            write_xmp(new_target_filename, data)
        else:
            write_xmp(new_target_filename, data)

        image_for_tagging = ImgTag(
            filename=new_target_filename,  # The image file
            force_case="lower",  # Converts the case of all tags
            # Can be `None`, `"lower"`, `"upper"`
            # Default: None
        )
        image_for_tagging.set_tags(special_award_tags)
        del(image_for_tagging)




    # if it's a project image, this secrtion makes sure a project description and title is incorporated
    if category == "P1" or category == "P2":
        # If the image is a project category then get the title and description from the spreadsheet
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

        # whatever image it is in the project, make sure
        desc_target_filename =  os.path.join(target_directory, '00_project_description.jpg')
        new_desc_target_filename =  os.path.join(new_target_directory, '00_project_description.jpg')

        # if we're not on a dry run the create the project description if it doesn't already exist and also write the metadata to the project description
        if not dryrun and in_second_round:
            if not os.path.isfile(new_desc_target_filename):
                project_text(title, description, new_desc_target_filename)
                if not anon:
                    data = {
                      'Rating': rating,
                      'Label': label,
                      'Title': title,
                      'Description': description,
                      'Rights': country,
                      'Creator': name,
                        'City': raw_score,
                    }
                else:
                    data = {
                    'Label': label,
                      'Rating': rating,
                    }
                write_xmp(new_desc_target_filename, data)
            else:
                if not os.path.isfile(desc_target_filename):
                    project_text(title, description, desc_target_filename)
                if not anon:
                    data = {
                      'Rating': rating,
                      'Label': label,
                      'Title': title,
                      'Description': description,
                      'Rights': country,
                      'Creator': name,
                        'City': raw_score,
                    }
                else:
                    data = {
                    'Label': label,
                      'Rating': rating,
                    }

                write_xmp(desc_target_filename, data)



    # Don't score portfolio catalogs based on aerial, nightscape or projects
    # Personally I think it should report which category it is in and still include the aerial and nightscape categoris
    if category == "P1" or category == "P2":
        return None, None
    else:

        # print('checking entry %s by %s'%(int(entry_id),int(id)))
        # if int(id) in port_id_list:
        #     print('matched user %s'%int(id))
        # if int(entry_id) in port_scores_by_entry_id.keys():
        #     print('matched entry_id %s'%int(entry_id))
        # this is for the portfolio category
        print(id, port_scores_by_entry_id.get(id,'no'),port_data.get(int(id),'no'))
        if int(id) in port_id_list and int(entry_id) in port_scores_by_entry_id.keys() and (int(id) in skip_project or port_data[int(id)] >= portfolio_min_score):

            port_score = port_data[int(id)]

            # copy target_filename to
            port_target_directory = os.path.join(new_target, 'portfolio', '{:0>4.1f}-{}'.format(port_score,id))
            Path(port_target_directory).mkdir(parents=True, exist_ok=True)

            port_target_filename =  os.path.join(port_target_directory, anon_filename)

            if get_raws and in_second_round:
                for f in efiles:
                    save_raw_from_url(cache_directory, target_directory, port_target_directory, anon_prefix, 'https://submit.naturallandscapeawards.com%s'%f, f.split('/')[-1], category, directory, id, rating, label, title, description, city, name, rawchecking)

            if not dryrun and ( not os.path.isfile(port_target_filename) or os.path.getsize(port_target_filename) < 100):
                image = Image.open(original_filename)
                # **************************************************************************************************************************
                image.thumbnail((4000, 4000))
                #image.thumbnail((1024,768))
                try:
                    image_conv = convert_to_srgb(image)
                except:
                    image_conv = image
                # **************************************************************************************************************************
                image_conv.save(port_target_filename, quality=94, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))
                #image_conv.save(target_filename, quality=70, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))
                image.close()
                if not anon:
                    data = {
                      'Rating': rating,
                      'Label': label,
                      'Title': title,
                      'Description': description,
                      'Rights': country,
                      'Creator': name,
                        'City': raw_score
                    }
                else:
                    data = {
                    'Label': label,
                    'Description': description,
                    'Title': title,
                      'Rating': rating,
                        'City': raw_score,
                        'Creator': '',
                    }
                if not dryrun:
                    write_xmp(port_target_filename, data)
            else:
                if not anon:
                    data = {
                      'Rating': rating,
                      'Label': label,
                      'Title': title,
                      'Description': description,
                      'Rights': country,
                      'Creator': name,
                        'City': raw_score
                    }
                else:
                    data = {
                    'Label': label,
                    'Description': description,
                    'Title': title,
                      'Rating': rating,
                        'City': raw_score,
                        'Creator': '',
                    }
                if not dryrun:
                    write_xmp(port_target_filename, data)

        return org_scores, judge_scores

#################################################################


if __name__ == "__main__":



    ## generate the catalog images for individual judges
    # python3.9 final-scores-full.py --judge=PZ --anon=True

    ## Get extra raws - this allows me to export my raw checking labels and have them reapplied
    ## If I don't have this, I can't regenerate the metadata as it blats my raw checking colour labels
    # python3.9 final-scores-full.py --raws=True --rawcheckcsv=TimParkin-rawchecking2edit.csv


    # A little bit of code to help Rajesh so he doesn't have to enter arguments
    # For me,
    # directory = where the csv's are (judges-csvs)
    # source = ../photos
    # entries_from_server = nlpa_combined_entries-final-cleaned-extra-COMBINED.csv
    # hence
    # python . ../photos nlpa_combined_entries-final-cleaned-extra-COMBINED.csv
    #
    # try:
    #     directory=sys.argv[1]
    #     source = sys.argv[2]
    #     entries_from_server = sys.argv[3]
    # except:
    #     directory = os.getcwd()
    #     source = '../ORIGINAL_FILES'
    #     entries_from_server = 'nlpa_combined_entries_2022_10_21-getall.csv'
    #


    import argparse
    import yaml
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", help="reference directory", default=os.getcwd())
    parser.add_argument("--originals", help="original source files")
    parser.add_argument("--full_csv", help="master data csv")
    parser.add_argument("--judge", help="judge specific output", default=None)
    parser.add_argument("--comparison", help="comparison data in state, city and country etc", default=False)
    parser.add_argument("--anon", help="make anonymous", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--raws", help="process raw files", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--rawcheckcsv", help="use csv backup of raw labels", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--dryrun", help="don't process images", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--minscore", help="minimum score to include", type=int, default=0)
    parser.add_argument("--target_base", help="base target directory name")
    # parser.add_argument("--filter_projects", help="list of project category names", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--portfolio_module", help="filename for portfolio module", default=None)
    parser.add_argument("--portfolio_top", help="amount of portfolios to portfolio_out", default=None)
    parser.add_argument("--config", help="yaml config file", default="config.yaml")



    args = parser.parse_args()
    directory = args.directory
    source = args.originals
    full_csv = args.full_csv
    dryrun = args.dryrun
    get_raws = args.raws
    rawcsv = args.rawcheckcsv
    anon = args.anon
    minscore = args.minscore
    for_judge = args.judge
    comparison = args.comparison

    portfolio_module = args.portfolio_module
    portfolio_top = args.portfolio_top
    config = args.config



    with open(config) as f:
         yaml_data = yaml.safe_load(f)

    yaml_args = yaml_data['args']


    if not args.target_base:
        target_base = yaml_args.get('target_base')
    else:
        target_base = args.target_base
    source = yaml_args.get('originals', args.originals)
    full_csv = yaml_args.get('fullcsv', args.full_csv)





    judges_data = yaml_data['judges']

    cat_winners = yaml_data['cat_winners']
    special_winners = yaml_data['special_winners']
    poty_winners = yaml_data['poty']
    project_winners = yaml_data['projects']


    judge_names = {}
    for k,v in judges_data.items():
        judge_names[v] = k


    portfolio_module = yaml_args.get('portfolio_module')
    entries_from_server = yaml_args.get('fullcsv', args.full_csv)
    print('entries_from_server=',entries_from_server)

    portfolio_out = yaml_args.get('portfolio_module', portfolio_module)



    # Empty the Portfolio.py for first runs

    # set this to None for first runs

                # 'PZ': entry_score_lookup.get( (id, entry_id, 'paul'), 0),
                # 'AN': entry_score_lookup.get( (id, entry_id, 'alex'), 0),
                # 'DC': entry_score_lookup.get( (id, entry_id, 'davidc'), 0),
                # 'TB': entry_score_lookup.get( (id, entry_id, 'theo'), 0),
                # 'SM': entry_score_lookup.get( (id, entry_id, 'sarah'), 0),
                # 'DT': entry_score_lookup.get( (id, entry_id, 'davidt'), 0),
                # 'OH': entry_score_lookup.get( (id, entry_id, 'orsolya'), 0),
                # 'SB': entry_score_lookup.get( (id, entry_id, 'sandra'), 0),



    # set this to empty for first runs STILL NEED TO SET THIS UP IN COMMANDS


    xmp="""
    <x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 7.0-c000 1.000000, 0000/00/00-00:00:00        ">
     <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
      <rdf:Description rdf:about=""
        xmlns:xmp="http://ns.adobe.com/xap/1.0/"
        xmlns:tiff="http://ns.adobe.com/tiff/1.0/"
        xmlns:exif="http://ns.adobe.com/exif/1.0/"
        xmlns:aux="http://ns.adobe.com/exif/1.0/aux/"
        xmlns:exifEX="http://cipa.jp/exif/1.0/"
        xmlns:photoshop="http://ns.adobe.com/photoshop/1.0/"
        xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/"
        xmlns:stEvt="http://ns.adobe.com/xap/1.0/sType/ResourceEvent#"
        xmlns:dc="http://purl.org/dc/elements/1.1/"
        xmlns:crd="http://ns.adobe.com/camera-raw-defaults/1.0/"
        xmlns:crs="http://ns.adobe.com/camera-raw-settings/1.0/"
        xmp:Rating="{rating}"
        xmp:Label="{label}"
        crs:RawFileName="{filename}">
   <dc:title>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">{title}</rdf:li>
    </rdf:Alt>
   </dc:title>
   <dc:description>
    <rdf:Alt>
     <rdf:li xml:lang="x-default">{description}</rdf:li>
    </rdf:Alt>
   </dc:description>
    <Iptc4xmpCore:CreatorContactInfo rdf:parseType="Resource">
        <Iptc4xmpCore:CiAdrCity>{city}</Iptc4xmpCore:CiAdrCity>
     </Iptc4xmpCore:CreatorContactInfo>
      </rdf:Description>
     </rdf:RDF>
    </x:xmpmeta>
    """


    # We input some settings that are compiled as the output of this code - easier than iterating back again over the whole code
    # These are essentially a list of summated portfolio scores and also a list of all portfolio individual scores.
    # Only used to compile the best portfolio selection
    from portfolio import port_ids, scores_dict

    # set these all to False for first runs

    # Compile the portfolio info into an id list. port is short for portfolio
    port_data = {}
    port_id_list = []

    for r in port_ids:
        port_data[int(r[0])] = r[1]
        port_id_list.append(int(r[0]))

    port_scores_by_entry_id = {}
    for user_id, score_data in scores_dict.items():
        for entry_id, score in score_data['scores'].items():
            port_scores_by_entry_id[int(entry_id)] = float(score)






    # project fonts
    title_font = ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 64)
    body_font = ImageFont.truetype('assets/GrotaSansAltRd-Medium.otf', 35)

    # These help us show the raw score rather than the adjusted score. See scoring code
    label_lookup = {
    5: 'Green',
    4: 'Yellow',
    3: 'Red',
    2: 'Blue',
    1: 'Purple',
    0: 'Grey',
    }


    # look up table for the judges lightroom catalog
    category_lookup = {
    'GS': '1 - Grand Scenic',
    'IL': '2 - Intimate Landscape',
    'A': '3 - Abstract and Details',
    'P1': '4 - Project',
    'P2': '4 - Project',
    'DL': 'Desert Landscapes',
    'S': 'Seascapes',
    'RG': 'Rocks and Geology',
    'FW': 'Frozen Worlds',
    'M': 'Mountains',
    'IB': 'In Your Backyard',
    'TL': 'Tropical Landscapes',
    'WL': 'Woodland',
    }
    primary = "Primary (grade all)"
    secondary = "Secondary (optional extras)"

    # primary = "Results"
    # secondary = "Results-secondary"

    # label lookup for categories if we're in the portfolio SECTION
    category_label_lookup = {
    'GS': 'Blue',
    'IL': 'Green',
    'A': 'Red',
    }

    # printing lowercase
    letters = string.ascii_lowercase


    # START OF ACTUAL PROCESSING

    df = pd.read_csv(entries_from_server)

    alex_scores = pd.read_csv('data/round_1_alex.csv', keep_default_na=False)
    tim_scores = pd.read_csv('data/round_1_tim.csv', keep_default_na=False)
    matt_scores = pd.read_csv('data/round_1_matt.csv', keep_default_na=False)
    rajesh_scores = pd.read_csv('data/round_1_rajesh.csv', keep_default_na=False)
    palmer_scores = pd.read_csv('data/round_1_palmer.csv', keep_default_na=False)

    tim_adjust = pd.read_csv('data/timadjust.csv', keep_default_na=False)
    matt_adjust = pd.read_csv('data/mattadjust.csv', keep_default_na=False)
    alex_adjust = pd.read_csv('data/alexadjust.csv', keep_default_na=False)
    palmer_adjust = pd.read_csv('data/palmeradjust.csv', keep_default_na=False)
    rajesh_adjust = pd.read_csv('data/rajeshadjust.csv', keep_default_na=False)
    tim_adjust_final = pd.read_csv('data/timadjust-final.csv', keep_default_na=False)

    organiser_score_set = {'N': alex_scores, 'Y': matt_scores, 'T': tim_scores, 'R': rajesh_scores,
                 'M': palmer_scores}

    adjust_set = {'Y': matt_adjust, 'T': tim_adjust, 'N': alex_adjust, 'M': palmer_adjust,
                  'R': rajesh_adjust, 'final': tim_adjust_final}




    judge_score_set = {
        'M': pd.read_csv('data/secondround-annamorgan.csv',keep_default_na=False),
        'H': pd.read_csv('data/secondround-hougaardmalan.csv',keep_default_na=False),
        'L': pd.read_csv('data/secondround-jacklodge.csv',keep_default_na=False),
        'R': pd.read_csv('data/secondround-jenniferrenwick.csv',keep_default_na=False),
        'P': pd.read_csv('data/secondround-mattpalmer.csv',keep_default_na=False),
    }


    tim_rawchecking = pd.read_csv('data/rawchecking-timparkin.csv')
    matt_rawchecking = pd.read_csv('data/rawchecking-mattpayne.csv')

    rawchecking_set = {'T': tim_rawchecking, 'Y': matt_rawchecking}




    if get_raws and False:
        tim_raw_labels = pd.read_csv(rawcsv,keep_default_na=False)
    else:
        tim_raw_labels = False

    extras_set = {}

    space = 0

    # headers = File name	Folder	Path	Flag	Label	Rating	Color Name

    R = {
    '* ': 1,
    '* * ': 2,
    '* * * ': 3,
    '* * * * ': 4,
    '* * * * * ': 5,
    '': 0,
    }

    project_score_lookup = {}
    project_label_lookup = {}

    entry_score_lookup = {}
    entry_label_lookup = {}

    project_adjust_lookup = {}
    entry_adjust_lookup = {}

    judge_project_score_lookup = {}
    judge_entry_score_lookup = {}

    ids_in_finals = set()






    # Get the base directory and the target directory
    base = os.path.join(directory, source)

    # This is the cache directory



    if for_judge:
        new_target = os.path.join(directory,'%s-%s'%(target_base,judge_names[for_judge]))
    else:
        new_target = os.path.join(directory, target_base)


    # print('source directory = %s'%source)
    # print('base target = %s'%target)
    # print('target directory = %s'%new_target)



    # GET ALL OF THE JUDGES AND ORGANISER SCORES
    for judge_id, score in judge_score_set.items():

        for i in range(len(score)):
            r = score.loc[i]
            if r['File,name'] == "00_project_description.jpg":
                continue
            user_id, entry_id = [int(x) for x in r['File,name'][:-4].rsplit('__', maxsplit=2)[1:]]

            # if entry_id in missing_ids:
            #     print('in score_set {}'.format(entry_id))
            ids_in_finals.add(entry_id)
            if (r['File,name'] == '00_project_description.jpg'):
                user_id = int(r['Folder'])
                if r['Path'].startswith('/'):
                    project_section = r['Path'].split('/')[-3]
                else:
                    project_section = r['Path'].split('\\')[-3]
                judge_project_score = float(R[r['Rating']])

                judge_project_score_lookup[ (str(user_id), str(project_section), judge_id) ] = project_score

            else:
                user_id, entry_id = [int(x) for x in r['File,name'][:-4].rsplit('__', maxsplit=2)[1:]]
                judge_entry_score = float(R[r['Rating']])
                judge_entry_score_lookup[ (str(user_id), str(entry_id), judge_id) ] = judge_entry_score

    judged_entry_ids = {}
    organiser_entry_score_lookup = {}
    organiser_entry_label_lookup = {}
    organiser_project_score_lookup = {}

    for judge_id, score in organiser_score_set.items():

        for i in range(len(score)):
            r = score.loc[i]
            if r['File,name'] == "00_project_description.jpg":
                user_id = int(r['Folder'])
                if r['Path'].startswith('/'):
                    project_section = r['Path'].split('/')[-3]
                else:
                    project_section = r['Path'].split('\\')[-3]
                project_score = float(R[r['Rating']])
                project_label = r['Color,Name']
                organiser_project_score_lookup[ (str(user_id), str(project_section), judge_id) ] = project_score
            else:
                user_id, entry_id = [int(x) for x in r['File,name'][:-4].rsplit('__', maxsplit=2)[1:]]
                o_score = float(R[r['Rating']])
                organiser_entry_score_lookup[ (str(user_id), str(entry_id), judge_id) ] = o_score
                organiser_entry_label_lookup[ (str(user_id), str(entry_id), judge_id) ] = r['Color,Name']
                judged_entry_ids[ str(entry_id) ] = True

    organiser_project_adjust_lookup = {}
    organiser_project_adjust_label_lookup = {}
    organiser_entry_adjust_lookup = {}
    organiser_entry_adjust_label_lookup = {}
    organiser_entry_adjust_rating_lookup = {}

# Loop on the adjustment items
    for judge_id, score in adjust_set.items():
        count = 0
        for i in range(len(score)):
            r = score.loc[i]

            if (r['File,name'] == '00_project_description.jpg'):


                f = r['Folder']
                if '-' in f:
                    user_id = int(r['Folder'].split('-')[1])
                    project_section = int(r['Folder'].split('-')[1])
                else:
                    user_id = int(r['Folder'].split('/')[2])
                    project_section = int(r['Folder'].split('/')[1].lstrip("0"))




                project_adjust = int(r['Flag'])
                project_label = r['Color,Name']
                # if int(project_adjust) != 0 :
                #     print('user_id %s, project_adjust %s'%(user_id, project_adjust))
                #     print(user_id,project_section, project_adjust)
                organiser_project_adjust_lookup[ (str(user_id), str(project_section), judge_id) ] = project_adjust
                organiser_project_adjust_label_lookup[ (str(user_id), str(project_section), judge_id) ] = project_label

                if judge_id not in ['T','final']:
                    if (str(user_id), str(project_section), judge_id) in organiser_project_score_lookup:
                        organiser_project_score_lookup[(str(user_id), str(project_section), judge_id)] += project_adjust
                    else:
                        organiser_project_score_lookup[(str(user_id), str(project_section), judge_id)] = project_adjust
            else:
                user_id, entry_id = [int(x) for x in r['File,name'][:-4].rsplit('__', maxsplit=2)[1:]]

                entry_adjust = int(r['Flag'])
                entry_label = r['Color,Name']
                entry_rating = float(R[r['Rating']])

                organiser_entry_adjust_lookup[ (str(user_id), str(entry_id), judge_id) ] = entry_adjust

                if judge_id not in ['T', 'final']:
                    organiser_entry_score_lookup[(str(user_id), str(entry_id), judge_id)] = entry_rating

                if (str(user_id), str(entry_id)) not in organiser_entry_adjust_label_lookup:
                    organiser_entry_adjust_label_lookup[(str(user_id), str(entry_id))] = {}
                organiser_entry_adjust_label_lookup[(str(user_id), str(entry_id))][judge_id] = entry_label



    # RAW CHECKING CSV SET

    entry_rawchecking_lookup = {}
    project_rawchecking_lookup = {}

    for judge_id, rawchecking in rawchecking_set.items():
        for i in range(len(rawchecking)):
            r = rawchecking.loc[i]

            if '-RAW' in r['File,name']:
                continue
            if (r['File,name'] == '00_project_description.jpg'):
                project_label = r['Label']
                f = r['Folder']
                if '-' in f:
                    user_id = int(r['Folder'].split('-')[1])
                    project_section = int(r['Folder'].split('-')[1])
                else:
                    user_id = int(r['Folder'].split('/')[2])
                    project_section = int(r['Folder'].split('/')[1].lstrip("0"))

                if (str(user_id), str(project_section), judge_id) in project_rawchecking_lookup:
                    max_project_label = project_rawchecking_lookup[ (str(user_id), str(project_section)) ]
                    if max_project_label == 'Green' and project_label != 'Green':
                        max_project_label = project_label
                    elif max_project_label == 'Yellow' and project_label == 'Red':
                        max_project_label = 'Red'

                    project_rawchecking_lookup[(str(user_id), str(project_section))] = max_project_label
                else:
                    project_rawchecking_lookup[(str(user_id), str(project_section))] = project_label


            else:
                user_id, entry_id = [int(x) for x in r['File,name'][:-4].rsplit('__', maxsplit=2)[1:]]
                entry_label = r['Label']

                if (str(user_id), str(entry_id), judge_id) in entry_rawchecking_lookup:
                    max_entry_label = entry_rawchecking_lookup[ (str(user_id), str(entry_id)) ]
                    if max_entry_label == 'Green' and entry_label != 'Green':
                        max_entry_label = entry_label
                    elif max_entry_label == 'Yellow' and entry_label == 'Red':
                        max_entry_label = 'Red'
                    entry_rawchecking_lookup[(str(user_id), str(entry_id))] = max_entry_label
                else:
                    entry_rawchecking_lookup[(str(user_id), str(entry_id))] = entry_label




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




    extra_lookup = {}
    extras_in_finals = set()



    judged_entry_ids = judged_entry_ids.keys()

    score_set = []
    space = 0
    user_scores = {}


    organiser_variance_totals = {
                'N': 0,
                'Y': 0,
                'T': 0,
                'R': 0,
                'M': 0,
            }

    entrants_by_entry_id = {}
    entrants_by_id = {}

    # MAIN LOOP  CHECK IN SECOND ROUND!!!
    for i in range(len(df)):
        printProgressBar(i + 1, len(df), prefix = 'Progress:', suffix = 'Complete', length = 80)
        row = df.loc[i]







        url = 'https://submit.naturallandscapeawards.com/%s' % row['entry_url']
        if not isinstance(url, str):
            continue
        filename = str(row['entry_filename'])
        if 'entries' in filename:
            filename = filename.split('/')[-1]
        parse_object = urlparse(url)
        noclash_filename = basename(parse_object.path)






        # GET ID and ENTRY_ID
        try:
            id = int(row['id'])
        except ValueError:
            continue
            
                    
        entry_id = int(row['entry_id'])



        country = row['country']
        in_second_round = row['in_second_round']




        # if entry_id not in ids_in_finals and entry_id not in extras_in_finals:
        #     continue

        if not isinstance(url,str):

            print('url not string')
            print(url)
            continue
        name = row['name']
        category = row['entry_category']
        size = row['entry_photo_size']
        if not isinstance(category, str):
            category = 'undefined'

        if id not in entrants_by_id:
            entrants_by_id[ id ] = row


        if id not in entrants_by_entry_id:
            entrants_by_entry_id[ entry_id ] = row


    import csv, math
    import pycountry_convert as pc





    country_count = {}
    with open('winners.csv', mode='w') as p:
        writer = csv.writer(p, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            'category',
            'id',
            'entry_id',
            'filename',
            'url',
            'prize',
            'name',
            'email',
            'country',
            'facebook',
            'instagram',
            'website',
            'bio',
            ])

        with open('pressrelease_entries.csv', mode='w') as p:
            writer_pr = csv.writer(p, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

            writer_pr.writerow([
                'name',
                'category',
                'placing',
                'email',
                'id',
                'entry_id',
                'filename',
                'url',
            ])

            print('MAIN PRIZES')
            for c, w in cat_winners.items():
                for id, prize in w.items():

                    e = entrants_by_entry_id[id]
                    country = e['country']
                    if not isinstance(country, str):
                        country = ''
                    else:
                        country = pc.country_alpha2_to_country_name(e['country'])

                    if country in country_count:
                        country_count[ country ] += 1
                    else:
                        country_count[ country ] = 1
                    print('%s: %s = %s [%s,%s] (%s)'%(category_lookup[c][4:],prize,e['name'],int(e['id']),id,country))
                    newname = '%s_%s_%s_%s_%s'%(category_lookup[c][4:],prize,e['name'],int(e['id']),id)
                    writer.writerow([
                        category_lookup[c][3:],
                        int(e['id']),
                        int(e['entry_id']),
                        e['entry_filename'],
                        e['entry_url'],
                        prize,
                        e['name'],
                        e['email'],
                        e['country'],
                        e['facebook'],
                        e['instagram'],
                        e['website'],
                        e['bio'],
                    ])
                    writer_pr.writerow([
                        e['name'],
                        category_lookup[c][3:],
                        prize,
                        e['email'],
                        int(e['id']),
                        int(e['entry_id']),
                        e['entry_filename'],
                        'https://submit.naturallandscapeawards.com/%s' % e['entry_url'],
                    ])

                    directory = e['entry_category']
                    saveimage(e,base,newname, directory)

            print('\nPHOTOGRAPHER OF THE YEAR')
            for id, data in poty_winners.items():
                prize = data['id']
                entries = data['entries']
                e = entrants_by_id[id]
                country = e['country']
                if not isinstance(country, str):
                    country = ''
                else:
                    country = pc.country_alpha2_to_country_name(e['country'])
                if country in country_count:
                    country_count[ country ] += 1
                else:
                    country_count[ country ] = 1
                print('poty: %s = %s [%s] (%s)'%(prize.split(',')[1],e['name'],id,country))
                writer.writerow([
                    "Photographer of the Year",
                    int(e['id']),
                    int(e['entry_id']),
                    e['entry_filename'],
                    e['entry_url'],
                    prize.split(',')[1],
                    e['name'],
                    e['email'],
                    e['country'],
                    e['facebook'],
                    e['instagram'],
                    e['website'],
                    e['bio'],
                ])



                for entry_id in entries:
                    entry = entrants_by_entry_id[entry_id]
                    directory = entry['entry_category']
                    newname = 'poty_%s_%s_%s' % (prize.split(',')[1], e['name'], id)
                    saveimage(entry, base, newname, directory, entry_id)
                    # try:
                    #     saveimage(e, base, newname, directory)
                    # except:
                    #     print('not found')
                    url = 'https://submit.naturallandscapeawards.com/%s' % entry['entry_url']
                    filename = str(row['entry_filename'])
                    writer_pr.writerow([
                        e['name'],
                        "Photographer of the Year",
                        prize,
                        e['email'],
                        int(e['id']),
                        entry_id,
                        filename,
                        url,
                    ])

            print('\nPROJECT OF THE YEAR')
            for id, data in project_winners.items():
                print(id)
                prize = data['id']
                entries = data['entries']
                e = entrants_by_id[int(id.split('-')[1])]
                country = e['country']
                if not isinstance(country, str):
                    country = ''
                else:
                    country = pc.country_alpha2_to_country_name(e['country'])
                if country in country_count:
                    country_count[ country ] += 1
                else:
                    country_count[ country ] = 1
                print('project: %s = %s [%s] (%s)'%(prize.split(',')[1],e['name'],id,country))
                newname = 'project_%s_%s' % (prize.split(',')[1], e['name'])
                writer.writerow([
                    "Projects",
                    int(e['id']),
                    int(e['entry_id']),
                    e['entry_filename'],
                    e['entry_url'],
                    prize.split(',')[1],
                    e['name'],
                    e['email'],
                    e['country'],
                    e['facebook'],
                    e['instagram'],
                    e['website'],
                    e['bio'],
                ])


                directory = 'P%s'%id.split('-')[0]

                for entry_id in entries:
                    entry = entrants_by_entry_id[entry_id]
                    directory = entry['entry_category']
                    newname = 'projects_%s_%s_%s' % (prize.split(',')[1], e['name'], id)
                    saveimage(entry, base, newname, directory, entry_id)
                    # try:
                    #     saveimage(e, base, newname, directory)
                    # except:
                    #     print('not found')
                    url = 'https://submit.naturallandscapeawards.com/%s' % entry['entry_url']
                    filename = str(row['entry_filename'])
                    writer_pr.writerow([
                        e['name'],
                        "Projects",
                        prize,
                        e['email'],
                        int(e['id']),
                        entry_id,
                        filename,
                        url,
                    ])



            print('\nSPECIAL CATEGORIES')
            for c, w in special_winners.items():
                print('')
                for id, prize in w.items():
                    e = entrants_by_entry_id[id]
                    country = e['country']
                    if not isinstance(country, str):
                        country = ''
                    else:
                        country = pc.country_alpha2_to_country_name(e['country'])

                    if country in country_count:
                        country_count[ country ] += 1
                    else:
                        country_count[ country ] = 1
                    print('%s: %s = %s [%s,%s] (%s)'%(c,prize,e['name'],int(e['id']),id,country))
                    newname = 'SPECIAL_%s_%s_%s_%s_%s' % (c,prize, e['name'],int(e['id']),id)
                    writer.writerow([
                        c,
                        int(e['id']),
                        int(e['entry_id']),
                        e['entry_filename'],
                        e['entry_url'],
                        prize,
                        e['name'],
                        e['email'],
                        e['country'],
                        e['facebook'],
                        e['instagram'],
                        e['website'],
                        e['bio'],
                    ])
                    writer_pr.writerow([
                        e['name'],
                        category_lookup[c],
                        prize,
                        e['email'],
                        int(e['id']),
                        int(e['entry_id']),
                        e['entry_filename'],
                        'https://submit.naturallandscapeawards.com/%s' % e['entry_url'],
                    ])

                    directory = e['entry_category']
                    saveimage(e, base, newname, directory)
                    # try:
                    #     saveimage(e, base, newname, directory)
                    # except:
                    #     print('not found')

    for k,v in country_count.items():
        print('%s = %s'%(v,k))
