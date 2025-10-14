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

import io
from PIL import Image
from PIL import ImageCms
import sys

from urllib.parse import urlparse
from posixpath import basename, dirname
import datetime

# This is the master first round processing engine from 2022
# The lightroom catalog is "test1" from the directory above ../test-catalogs/test1

# from portfolio import port_ids, scores_dict
#
# port_data = {}
# port_id_list = []
# for r in port_ids:
#     port_data[int(r[0])] = r[1]
#     port_id_list.append(int(r[0]))
#
# port_scores_by_entry_id = {}
# for user_id, score_data in scores_dict.items():
#     for entry_id, score in score_data['items'].items():
#         port_scores_by_entry_id[int(entry_id)] = float(score)

#print(port_scores_by_entry_id)

category_score_threshold = {
    'GS': 3.0,
    'IL': 3.2,
    'AD': 2.4,
}




# directory is used as base for target and source
# source should be the raw downloads, target the directory to place the scored images in

try:
    directory=sys.argv[1]
    source = sys.argv[2]
except:
    directory = '/Users/timparkin/nlpa-2025/'
    source = 'ORIGINALS'

base = os.path.join(directory,source)
root_directory = directory
target = os.path.join(directory, 'Master Finals NOTANON')

label_lookup = {
5: 'Red',
4: 'Yellow',
3: 'Green',
2: 'Blue',
1: 'Purple',
0: 'Grey',
}


category_lookup = {
'GS': '1 - Grand Scenic',
'IL': '2 - Intimate Landscape',
'AD': '3 - Abstract and Details',
'P1': '4 - Project',
'P2': '4 - Project',
}


primary = "1 - Primary"
maybe_primary = "2 - Optional"
secondary = "3 - Secondary"



MAKE_ANONYMOUS = False



df = pd.read_csv('data/nlpaentries.csv')
alex_scores = pd.read_csv('data/round_1_alex.csv',keep_default_na=False)
tim_scores = pd.read_csv('data/round_1_tim.csv',keep_default_na=False)
matt_scores = pd.read_csv('data/round_1_matt.csv',keep_default_na=False)
rajesh_scores = pd.read_csv('data/round_1_rajesh.csv',keep_default_na=False)
palmer_scores = pd.read_csv('data/round_1_palmer.csv',keep_default_na=False)

tim_adjust = pd.read_csv('data/timadjust.csv',keep_default_na=False)
matt_adjust = pd.read_csv('data/mattadjust.csv',keep_default_na=False)
alex_adjust = pd.read_csv('data/alexadjust.csv',keep_default_na=False)
palmer_adjust = pd.read_csv('data/palmeradjust.csv',keep_default_na=False)
rajesh_adjust = pd.read_csv('data/rajeshadjust.csv',keep_default_na=False)
tim_adjust_final = pd.read_csv('data/timadjust-final.csv',keep_default_na=False)

score_set = {'N': alex_scores, 'Y': matt_scores, 'T': tim_scores, 'R': rajesh_scores, 'M': palmer_scores}

adjust_set = {'Y': matt_adjust, 'T': tim_adjust, 'N': alex_adjust, 'M': palmer_adjust, 'R': rajesh_adjust}






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






def score_var_calc(scoresx):


    # if scoresx[3]>3:
    #     r = scoresx[3]-1
    # else:
    #     r = scoresx[3]
    # scores = [scoresx[0],scoresx[1],scoresx[2],r]
    # sort scores to low first



    scores = [scoresx[0],scoresx[1],scoresx[2],scoresx[3],scoresx[4]]

    # sort scores to low first
    scores.sort()

    # get rid of lowest score
    scores_skiplow = scores[1:]
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
    raw_score = score









    if tops >= 2:
        score = 5.0

    elif tops >= 1:
        score = 4.666

    elif highs >= 2:
        score = 4.333

    elif highs >=1:
        score = 4.0



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

    #return score*3.0, raw_score, int(var)

    #tscore = (score*3.0)-10
    tscore = score

    #if tscore == 5:
        #print('FV %s %s %s'%(score, tscore,  raw_score))
    #if tscore == 4:
        #print('FR %s %s %s'%(score, tscore,  raw_score))
    #if tscore == 3:
        #print('TH %s %s %s'%(score, tscore,  raw_score))
    #else:
        #print('  %s %s %s'%(score, tscore,  raw_score))

    return tscore, raw_score, int(var)







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


#def write_xmp(path, data):
#    try:
#        I = pyexiv2.Image(path)
#        I.modify_xmp({'Xmp.xmp.Label': data.get('Label','')})
#        I.modify_xmp({'Xmp.xmp.Rating': str(data.get('Rating',0))})
#        I.modify_xmp({'Xmp.dc.title': {'lang="x-default"': data.get('Title','')}})
#        I.modify_xmp({'Xmp.dc.description': {'lang="x-default"': data.get('Description','')}})
#        I.close()
#    except RuntimeError:
#        pass
#        #print(path)
#    return

def write_xmp(path, data):
    if not MAKE_ANONYMOUS:
        try:
            metadata = pyexiv2.ImageMetadata(path)
            metadata.read()
            metadata['Xmp.xmp.Label'] = str(data.get('Label',''))
            metadata['Xmp.xmp.Rating'] = int(data.get('Rating',0))
            metadata['Xmp.xmp.Rating'] = int( round((data.get('State',2.4)-2.4)*2.083))

            metadata['Xmp.dc.title'] = data.get('Title','')
            metadata['Xmp.dc.description'] = data.get('Description','')
            metadata['Xmp.dc.creator'] = [data.get('Creator','')]
            metadata['Xmp.dc.rights'] = data.get('Creator','')
            metadata['Iptc.Application2.City'] = [str(round((data.get('State',2.4)-2.4)*2.083,3))]
            metadata['Exif.Image.DateTime'] = datetime.datetime(2025, 6, 21, 0, 0, 0) - datetime.timedelta(0,round((data.get('State',2.4)-2.4)*2.083,3)*1000)
            metadata['Iptc.Application2.ProvinceState'] = [str(data.get('State', ''))]
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
            metadata['Iptc.Application2.City'] = [str(round(data.get('State',2.4),3))]
            metadata['Iptc.Application2.ProvinceState'] = [str(round((data.get('State',2.4)-2.4)*2.083,3))]
            metadata.write()
        except RuntimeError:
            print(f'xmp runtime error {path}')
    return

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

def resize(filename, category, directory, entry_id, id, row, project_score_lookup, project_label_lookup, entry_score_lookup, entry_label_lookup, project_adjust_lookup, entry_adjust_lookup, project_adjust_label_lookup, entry_adjust_label_lookup):

    original_directory = os.path.join(base, category, directory)
    print('ORIGINALS',original_directory)

    try:
        if category == "P1" or category == "P2":
            entry_scores = {
                'N': project_score_lookup.get( (id, category, 'N'), 2),
                'Y': project_score_lookup.get( (id, category, 'Y'), 2),
                'T': project_score_lookup.get( (id, category, 'T'), 2),
                'R': project_score_lookup.get( (id, category, 'R'), 2),
                'M': project_score_lookup.get((id, category, 'M'), 2),
            }
            entry_labels = {
                'N': project_label_lookup.get( (id, category, 'N'), 2),
                'Y': project_label_lookup.get( (id, category, 'Y'), 2),
                'T': project_label_lookup.get( (id, category, 'T'), 2),
                'R': project_label_lookup.get( (id, category, 'R'), 2),
                'M': project_label_lookup.get((id, category, 'M'), 2),
            }
            scores_list = [entry_scores['N'],entry_scores['Y'],entry_scores['T'],entry_scores['R'],entry_scores['M'],]

            logging.debug(scores_list)

            mean_score, raw_score, svar = score_var_calc(scores_list)

            #return mean_score, raw_score, svar, scores_list

            if int(project_adjust_lookup.get( (id, category[1], 'T'),0 )) == -1:
                # print('adjusting- project score of %s --------'%entry_id)
                # print('old score',mean_score)
                mean_score = float(4)
                # print('new score',mean_score)
                svar=4

            if int(project_adjust_lookup.get( (id, category[1], 'T'),0 )) == 1:
                # print('adjusting+ project score of %s ++++++++'%entry_id)
                # print('old score',mean_score)
                mean_score = float(5)
                # print('new score',mean_score)
                svar=5

            project_adjust_label = project_adjust_label_lookup.get( (id, category[1], 'tim') )


        else:
            entry_scores = {
                'N': entry_score_lookup.get( (id, entry_id, 'N'), 2),
                'Y': entry_score_lookup.get( (id, entry_id, 'Y'), 2),
                'T': entry_score_lookup.get( (id, entry_id, 'T'), 2),
                'R': entry_score_lookup.get( (id, entry_id, 'R'), 2),
                'M': entry_score_lookup.get((id, entry_id, 'M'), 2),
            }
            entry_labels = {
                'N': entry_label_lookup.get( (id, entry_id, 'N'), 2),
                'Y': entry_label_lookup.get( (id, entry_id, 'Y'), 2),
                'T': entry_label_lookup.get( (id, entry_id, 'T'), 2),
                'R': entry_label_lookup.get( (id, entry_id, 'R'), 2),
                'M': entry_label_lookup.get((id, entry_id, 'M'), 2),
            }
            scores_list = [entry_scores['N'],entry_scores['Y'],entry_scores['T'],entry_scores['R'],entry_scores['M'],]


            # if scores_list == [3.0, 3.0, 4.0, 3.0, 3.0]:
            #     print(scores_list)

            if scores_list[2] == 5 and (scores_list.count(4) + scores_list.count(5)) == 1:
                scores_list[2] = 4.0
            if scores_list[2] == 4 and S.mean(scores_list) < 2.5:
                scores_list[2] = 3.0

            # if scores_list == [3.0, 3.0, 4.0, 3.0, 3.0]:
            #     print(scores_list)


            logging.debug(scores_list)
            # **************************************************************************************************************************
            mean_score, raw_score, svar = score_var_calc(scores_list)


            #return mean_score, raw_score, svar, scores_list
            # if scores_list == [3.0, 3.0, 4.0, 3.0, 3.0]:
            #     print(mean_score, raw_score, svar)



            if int(entry_adjust_lookup.get( (id, entry_id, 'T'),0 )) == -1:
                #print('adjusting entry score of %s --------'%entry_id)
                mean_score = float(3)
                svar = 5

            if int(entry_adjust_lookup.get( (id, entry_id, 'T'),0 )) == 1:
                #print('adjusting entry score of %s +++++++++'%entry_id)
                mean_score = float(3.5)
                svar = 3

            entry_adjust_label = entry_adjust_label_lookup.get( (id, entry_id, 'T'))

            # if scores_list == [3.0, 3.0, 4.0, 3.0, 3.0]:
            #     print(mean_score, raw_score, svar)
            #     sys.exit()

    except KeyError as e:
        sys.exit()
        logging.error("ERROR %s"%e)
        print('key error')
        return None, None, None, None




    #return mean_score, raw_score, svar
    # ***********************************************

    #if mean_score < 0:
    # if mean_score < 0 and entry_id not in [6666666666,77777777777]:
    #     return None,None,None

    # if mean_score <2:
    #     mean_score += 1

    logging.debug('mean =%s, raw =%s, var = %s'%(mean_score,raw_score,svar))




    if category == "P1" or category == "P2":
        composite_score = (float(mean_score)-1.0)+(svar/5.0)
        logging.debug('composite score %s'%composite_score)
        # if composite_score<2:
        #     return None, None, None
        # else:
        #     return mean_score, raw_score, svar



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



        if mean_score>4 and raw_score >= 3:
            target_directory = os.path.join(target, primary, category_lookup[category], '%s-%s-%s'%(int(round(raw_score,2)*100),category[1],id))
        else:
            target_directory = os.path.join(target, secondary, category_lookup[category], '%s-%s-%s'%(int(round(raw_score,2)*100),category[1],id))
        cache_directory = os.path.join(os.getcwd(), 'cache', category_lookup[category])


    else:
        if entry_labels['T'] == 'green' or entry_labels['n'] == 'green' or entry_labels['Y'] == 'green' or entry_labels['M'] == 'green':
            category = 'GS'
        if entry_labels['T'] == 'yellow' or entry_labels['N'] == 'yellow' or entry_labels['Y'] == 'yellow' or entry_labels['M'] == 'yellow':
            category = 'IL'
        if entry_labels['T'] == 'red' or entry_labels['N'] == 'red' or entry_labels['Y'] == 'red' or entry_labels['M'] == 'red':
            category = 'AD'

        if entry_adjust_label == 'green':
            category = 'GS'
        if entry_adjust_label == 'yellow':
            category = 'IL'
        if entry_adjust_label == 'red':
            category = 'AD'



        category_placement = category_lookup[category]



        if mean_score>4 or (mean_score>3 and raw_score>=category_score_threshold[category]):
            target_directory = os.path.join(target, primary, category_placement)

        elif mean_score>3:
            target_directory = os.path.join(target, maybe_primary, category_placement)

        else:
            target_directory = os.path.join(target, secondary, category_placement)

        cache_directory = os.path.join('cache', category_placement)

    Path(target_directory).mkdir(parents=True, exist_ok=True)
    Path(cache_directory).mkdir(parents=True, exist_ok=True)
    original_filename =  os.path.join(original_directory, filename)
    logging.info('original: %s'%original_filename)
    encoded_filename = str(entry_id)[::-1]
    #print('encodded: %s'%filename)
    anon_filename = '%s__%s__%s.jpg'%(encoded_filename,id,entry_id)
    target_filename =  os.path.join(target_directory, anon_filename)
    cache_filename = os.path.join(cache_directory, anon_filename)



    #label = label_lookup[svar]
    if scores_list.count(4) == 1 and scores_list.count(5) == 0:
        label = label_lookup[ scores_list.index(4)+1]
    else:
        label = 0

    if not os.path.isfile(cache_filename):
        image = Image.open(original_filename)
        # **************************************************************************************************************************
        #image.thumbnail((1000, 800))
        #image.thumbnail((2048, 1536))
        image.thumbnail((3456,2234))
        try:
            image_conv = convert_to_srgb(image)
        except:
            image_conv = image
        # **************************************************************************************************************************
        #image_conv.save(target_filename, quality=92, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))
        image_conv.save(cache_filename, quality=90, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))
        image.close()
        data = {
          'Rating': int(mean_score),
          'City': mean_score,
          'State': raw_score,
          'Creator': '%s <%s>'%(row['name'], row['email']),
          'Label': label,
                  'Title': '',
                  'Description': 'a:{:1.0f}, m:{:1.0f}, t:{:1.0f}, p:{:1.0f}, r:{:1.0f}\nmean_score={:1.2f}, raw_score={:1.2f}'.format(entry_scores['N'],entry_scores['Y'],entry_scores['T'],entry_scores['M'],entry_scores['R'],mean_score,raw_score),
        }
        write_xmp(cache_filename, data)
        shutil.copy2(cache_filename, target_filename)
    else:
        data = {
          'Rating': int(mean_score),
          'City': mean_score,
          'State': raw_score,
          'Creator': '%s <%s>'%(row['name'], row['email']),
          'Label': label,
                  'Title': '',
                  'Description': 'a:{:1.0f}, m:{:1.0f}, t:{:1.0f}, p:{:1.0f}, r:{:1.0f}\nmean_score={:1.2f}, raw_score={:1.2f}'.format(entry_scores['N'],entry_scores['Y'],entry_scores['T'],entry_scores['M'],entry_scores['R'],mean_score,raw_score),
        }
        write_xmp(cache_filename, data)
        shutil.copy2(cache_filename, target_filename)
        #print('** SKIPPING = %s'%target_filename)


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


        desc_target_filename =  os.path.join(target_directory, '00_project_description.jpg')
        if not os.path.isfile(desc_target_filename):
            project_text(title, description, desc_target_filename)
            data = {
              'Label': label,
              'Title': 'project',
            }
            write_xmp(desc_target_filename, data)

    # Return before calculating portfolio scores
    return mean_score, raw_score, svar, scores_list, category


    # if category == "P1" or category == "P2" :
    #     return None, None, None
    # else:
    #
    #
    #     if int(id) in port_id_list and int(entry_id) in port_scores_by_entry_id.keys():
    #         # copy target_filename to
    #         target_directory = os.path.join(target, 'portfolio', id)
    #         Path(target_directory).mkdir(parents=True, exist_ok=True)
    #         target_filename =  os.path.join(target_directory, anon_filename)
    #         if not os.path.isfile(target_filename):
    #             image = Image.open(original_filename)
    #             # **************************************************************************************************************************
    #             #image.thumbnail((3000, 3000))
    #             image.thumbnail((1024,768))
    #             try:
    #                 image_conv = convert_to_srgb(image)
    #             except:
    #                 image_conv = image
    #             # **************************************************************************************************************************
    #             #image_conv.save(target_filename, quality=94, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))
    #             image_conv.save(target_filename, quality=70, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))
    #             image.close()
    #             data = {
    #               'Rating': int(port_scores_by_entry_id[int(entry_id)]/3.0),
    #               'Label': label_lookup[svar],
    #               'Title': str(scores_dict[int(id)]['total']),
    #               'Description': '',
    #             }
    #             write_xmp(target_filename, data)
    #         else:
    #             data = {
    #               'Rating': int(port_scores_by_entry_id[int(entry_id)]/3.0),
    #               'Label': label_lookup[svar],
    #               'Title': str(scores_dict[int(id)]['total']),
    #               'Description': '',
    #             }
    #             write_xmp(target_filename, data)
    #
    #     return mean_score, raw_score, svar






space = 0

# headers = File,name	Folder	Path	Flag	Label	Rating	Color,Name

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
project_adjust_label_lookup = {}
entry_adjust_lookup = {}
entry_adjust_label_lookup = {}

for judge_id, score in score_set.items():
    count = 0
    for i in range(len(score)):
        r = score.loc[i]

        if (r['File,name'] == '00_project_description.jpg'):
            user_id = int(r['Folder'])

            if r['Path'].startswith('/'):
                project_section = r['Path'].split('/')[-3]
            else:
                project_section = r['Path'].split('\\')[-3]
            project_score = float(R[r['Rating']])
            project_label = r['Color,Name']

            if judge_id == 'N' and project_score == 0:
                project_score = float(1)

            project_score_lookup[ (str(user_id), str(project_section), judge_id) ] = project_score
            project_label_lookup[ (str(user_id), str(project_section), judge_id) ] = project_label

        else:
            user_id, entry_id = [int(x) for x in r['File,name'][:-4].rsplit('__', maxsplit=2)[1:]]
            entry_score = float(R[r['Rating']])
            if judge_id != 'palmer':
                entry_label = r['Color,Name']
            else:
                entry_label = 'gray'


            entry_score_lookup[ (str(user_id), str(entry_id), judge_id) ] = entry_score
            entry_label_lookup[ (str(user_id), str(entry_id), judge_id) ] = entry_label

for judge_id, score in adjust_set.items():
    count = 0
    for i in range(len(score)):
        r = score.loc[i]

        if (r['File,name'] == '00_project_description.jpg'):


            f = r['Folder']
            if '-' in f:
                user_id = int(r['Folder'].split('-')[2])
                project_section = int(r['Folder'].split('-')[1])
            else:
                user_id = int(r['Folder'].split('/')[2])
                project_section = int(r['Folder'].split('/')[1].lstrip("0"))




            project_adjust = int(r['Flag'])
            project_label = r['Color,Name']

            project_adjust_lookup[ (str(user_id), str(project_section), judge_id) ] = project_adjust
            project_adjust_label_lookup[ (str(user_id), str(project_section), judge_id) ] = project_label

        else:
            user_id, entry_id = [int(x) for x in r['File,name'][:-4].rsplit('__', maxsplit=2)[1:]]

            entry_adjust = r['Flag']
            if judge_id == 'final' or judge_id == 'tim':
                entry_label = r['Color,Name']
            else:
                entry_label = 'Gray'

            entry_adjust_lookup[ (str(user_id), str(entry_id), judge_id) ] = entry_adjust
            entry_adjust_label_lookup[ (str(user_id), str(entry_id), judge_id) ] = entry_label



score_set = []
space = 0
user_scores = {}


l = len(df)

results = {'GS': [], 'IL': [], 'AD': [], 'P1': [], 'P2': []}

for i in range(l):
    printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 80)
    row = df.loc[i]

    url = 'https://submit.naturallandscapeawards.com/%s'%row['entry_url']

    id = row['id']
    entry_id = row['entry_id']
    if not isinstance(url,str):
        continue
    filename = str(row['entry_filename'])
    if 'entries' in filename:
        filename = filename.split('/')[-1]


    parse_object = urlparse(url)
    noclash_filename = basename(parse_object.path)

    name = row['name']
    email = row['email']
    category = row['entry_category']
    if category == 'undefined':
        continue
    size = row['entry_photo_size']
    if not isinstance(category, str):
        logging.debug('category %s not string'%category)
        continue
    logging.debug('size=%s, name=%s, category=%s'%(size,name,category))
    if not math.isnan(size):
        try:
            mean_score, raw_score, var, scores_list, category = resize(noclash_filename, category, name, str(int(entry_id)), str(int(id)), row, project_score_lookup, project_label_lookup, entry_score_lookup, entry_label_lookup, project_adjust_lookup, entry_adjust_lookup, project_adjust_label_lookup, entry_adjust_label_lookup)
            if mean_score > 3:
                results[category].append({'mean': mean_score, 'raw': raw_score, 'scores': scores_list})
            logging.debug('%s,%s,%s,%s,%s'%(id,entry_id, mean_score, raw_score, var))
            if mean_score is not None:

                score_set.append(mean_score+10.0)

                if category not in ["P1","P2"]:
                    if id not in user_scores:
                        user_scores[id] = {'scores': {entry_id : mean_score}}
                    else:
                        user_scores[id]['scores'][entry_id] = mean_score




        except OSError as e:
            pass
            print(e)
            print('ERROR WITH %s for %s in %s (%s,%s)'%(noclash_filename,category,name,id,entry_id))
    else:
        pass
        print('error with size=%s. %s for %s in %s'%(size,noclash_filename,category,name))

from pprint import pprint

bins = {}
bins_total = {}
for category, scores in results.items():
    print(category, len(scores))


    count = len(scores)
    bin = {}

    for score in scores:
        mean = score['raw']
        bin.setdefault(mean,0)
        bin[mean] += 1
    bins[category] = bin

    bin_totals = {}
    for meana, counta in bin.items():
        for meanb, countb in bin.items():
            if meanb >= meana:
                bin_totals.setdefault(meana,0)
                bin_totals[meana] += countb
    bins_total[category] = bin_totals



pprint(bins)
pprint(bins_total)

for user_id, score_data in user_scores.items():
    total_scores = []
    for entry_id, score in score_data['scores'].items():
        total_scores.append((entry_id, score+10.0))
    total_scores.sort(key=lambda tup: tup[1], reverse=True)
    topsix = total_scores[:6]
    score_data['items'] = {}
    for t in topsix:
        score_data['items'][t[0]] = t[1]
    total = 0
    for s in total_scores[:6]:
        total += s[1]
    score_data['total'] = total/3.0



sorted_scores = []
for user_id, score_data in user_scores.items():
    sorted_scores.append( (user_id, score_data['total']) )
    sorted_scores.sort(key=lambda tup: tup[1], reverse=True)

#print("port_ids = [")
#for t in sorted_scores[:40]:
    #print("({0:}, {1:.2f}),".format(*t))
#print("]")

#print("scores_dict = ", end = '')
#print(user_scores)





import collections
#print(collections.Counter(score_set))
