from certs.certificates import build_cert
import os
import pandas as pd
import PIL
from PIL import Image, ImageFont, ImageDraw, ImageFilter
from PIL import Image
from PIL import ImageCms
from PIL.ExifTags import TAGS
import base64
from pathlib import Path

from .portfolio_out_all_2025 import port_ids, scores_dict
import io


import random
import pyexiv2
import csv
import sys
import json

import yaml

from final_scores import score_var_calc_judges, score_var_calc_org

import re

# Files Needed
#  - nlpa_combined_entries_2021.csv (export from get_raw.csv?get_all=true)
#  - projects_tweaked.csv (from project_stage_calc.py)
#  - everything_entries_secondaryonly.csv (jblistview export of all secondary files )
#  - all_photos_from_withraw.csv (jblistview every photo exported including caption field that shows the scores)

# e.g. python3.9 build_certs.py --config=config.yaml --skipexisting=True

build_projects = False


def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)




def process_caption(s, title, caption_sections):
    # caption_sample = Z1.N2.C1.B2.M2 P4.Y3.A3.O3
    # title_sample = m0 r2.6 v1.14
    #print(caption)
    j_scores= {
        s[0]:int(s[1]),
        s[3]:int(s[4]),
        s[6]:int(s[7]),
        s[9]:int(s[10]),
        s[12]:int(s[13]),
        }
    j_scores_list = [ int(s[1]), int(s[4]), int(s[7]), int(s[10]), int(s[13]) ]

    if 'country' in s:
        o_scores = {
            s[15]:int(s[16]),
            s[18]:int(s[19]),
            s[21]:int(s[22]),
            s[24]:int(s[25]),
            s[27]:int(s[28]),
            }
        o_scores_list = [ int(s[16]), int(s[19]), int(s[22]), int(s[25]),  int(s[28])]
    else:
        o_scores = {}
        o_scores_list = [0,0,0,0,0]

    try:
        if 'country' in s:
            mean_score, raw_score, variance = [float(t[1:]) for t in title.split(' ')]
        else:
            # 0 : 2.6 : 1.93
            mean_score, raw_score, variance = [float(t) for t in title.split(' : ')]
    except (ValueError, AttributeError):
        mean_score, raw_score, variance = 0, 0, 0

    return j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score



def process_secondary_caption(s, title, caption_sections):
    # caption_sample = a:5, m:5, t:3, p:4, r:5\nmean_score=3.67, raw_score=3.00
    # print(s)
    o_scores = {
        s[0]: int(s[2]),
        s[5]: int(s[7]),
        s[10]: int(s[12]),
        s[15]: int(s[17]),
        s[20]: int(s[22]),
        }
    o_scores_list = [ int(s[2]), int(s[7]), int(s[12]), int(s[17]), int(s[22]) ]

    j_scores = {
        caption_sections[0]: 0,
        caption_sections[1]: 0,
        caption_sections[2]: 0,
        caption_sections[3]: 0,
        caption_sections[4]: 0,
    }
    mean_score, raw_score = [float(part.split('=')[1]) for part in s.split('\n')[1].split(', ')]

    j_scores_list = [0,0,0,0,0]
    return j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score

def convert_to_srgb(img):
    '''Convert PIL image to sRGB color space (if possible)'''
    icc = img.info.get('icc_profile', '')
    if icc:
        io_handle = io.BytesIO(icc)     # virtual file
        src_profile = ImageCms.ImageCmsProfile(io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        img = ImageCms.profileToProfile(img, src_profile, dst_profile)
    else:
        dst_cms = ImageCms.createProfile('sRGB')
        dst_profile = ImageCms.ImageCmsProfile(dst_cms)
        iccbytes = dst_profile.tobytes()
        img.info['icc_profile'] = iccbytes

        print('no source')
    return img

def write_xmp(path, data):
    try:
        metadata = pyexiv2.ImageMetadata(path)
        metadata.read()
        metadata['Xmp.dc.title'] = data.get('Title','')
        metadata['Xmp.Iptc4xmpCore.CreatorContactInfo/Iptc4xmpCore:CiUrlWork'] = data.get('Website','')
        metadata['Xmp.dc.description'] = data.get('Description','')
        metadata['Xmp.dc.creator'] = [data.get('Creator','')]
        metadata['Xmp.dc.rights'] = data.get('Creator','')
        metadata.write()
    except RuntimeError:
        print(f'xmp runtime error {path}')

    return

# SOCIAL MEDIA IMAGES
def build_socialmedia(user_id, entry_id, entry_by_entry_id, f, scores, name, subheader, stage, is_portfolio, prize, year, cachedir, social_media_dir, batch=None):



    if name[0].isupper() and name[1].isupper() and name != "DCraig Young":
        # print(name)
        name = name.title()
        # print(name)

    if name[0].islower() and name[1].islower():
        # print(name)
        name = name.title()
        # print(name)

    cname = "©%s"%name
    offset = 0
    longedge = 3000

    entry = entry_by_entry_id[entry_id]

    social_media_dir=social_media_dir
    if not os.path.isdir(social_media_dir):
        Path(social_media_dir).mkdir(parents=True, exist_ok=True)

    mainimage = Image.open(f)
    main_width, main_height = mainimage.size


    full_height = 2048
    full_width = 2048


    facebook = entry['facebook']
    instagram = entry['instagram']
    bio = entry['bio']
    website = entry['website']
    user_id = str(user_id)
    if '_' in user_id:
        batch = int(user_id.split('_')[0])
    else:
        user_id = int(user_id)


    if batch == 1:
        title = entry['project_title_one']
        description = entry['project_description_one']
    elif batch == 2:
        title = entry['project_title_two']
        description = entry['project_description_two']
    else:
        title = ''
        description = ''

    print(title)

    description = f"""F: {facebook}
I: {instagram}
W: {website}

{bio}

---
Project: {title}
{description}
      
"""


    data = {
        'Label': '',
        'Rating': '',
        'Description': description,
        'Website': website,
        'Title': title,
        'City': '',
        'State': '',
        'Country': '',
        'Creator': f'{name}',
    }


    #
    #
    #  BUILD SOCIAL GENERIC
    #
    #

    if main_width > main_height:
        #scale_factor = main_height/main_width
        scale_factor = 1
    else:
        scale_factor = main_width/main_height

    # masterlogoimage = Image.open('nlpa-logo-800-2023.png')
    # master_logo_width, master_logo_height = masterlogoimage.size
    #
    #
    # logo_height = int(master_logo_height * scale_factor)
    # logo_width = int(master_logo_width * scale_factor)
    #
    # logoimage = masterlogoimage.resize((logo_width,logo_height))


    # Build main image
    if main_width > main_height:
        main_height = int((full_height / main_width) * main_height)
        main_width = 2048
    else:
        main_width = int(((2048) / main_height) * main_width)
        main_height = full_height




    # new_im = Image.new(mode="RGB", size=(main_width, main_height + logo_height), color='WHITE')
    # mainimage = mainimage.resize((main_width, main_height))
    #
    # new_im.putdata( mainimage.getdata() )
    # new_im.paste( logoimage,(0,main_height,logo_width,main_height+logo_height))


    # font_size = int(60*scale_factor)
    # tw, th = get_text_dimensions(cname, font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', font_size))
    #
    #
    # draw = ImageDraw.Draw(new_im)
    # draw.text((main_width-(tw+th*0.5)-offset+2,main_height-th*1.5+2),cname, fill='#000000',font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', font_size))
    # draw.text((main_width-(tw+th*0.5)-offset,main_height-th*1.5),cname, fill='#FFFFFF',font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', font_size))
    #

    # # CHANGE THE NAME TO USE ID, POHOTOGRAPHER NAME, SCORE, ETC
    # new_im.save(os.path.join(social_media_dir,str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-social.jpg'))
    #


    #
    #
    # Build insta image square
    # Build main image
    #
    #
    scalefactor = longedge/2000

    full_height = longedge
    full_width = longedge

    # logo_height = int(master_logo_height*scalefactor)
    # logo_width = int(master_logo_width*scalefactor)
    # logoimage = masterlogoimage.resize((logo_width,logo_height))

    image_canvas_height = full_height
    image_canvas_width = full_width

    if main_width > main_height:
        main_height = int((image_canvas_width / main_width) * main_height)
        main_width = image_canvas_width
    else:
        main_width = int(((image_canvas_height) / main_height) * main_width)
        main_height = image_canvas_height

    if batch == 1 or batch == 2 and build_projects is False:
        return

    new_im = Image.new(mode="RGB", size=(image_canvas_width,image_canvas_width), color='WHITE')
    mainimage = mainimage.resize((main_width, main_height))

    # now add blur background to mainimage
    if main_width<image_canvas_width:
        blur_width = image_canvas_width
        blur_height = int( (image_canvas_width/main_width) * main_height )
    elif main_height<image_canvas_height:
        blur_height = image_canvas_height
        blur_width = int( (image_canvas_width/main_height) * main_width )
    else:
        blur_width = main_width
        blur_height = main_height

    blurimage = mainimage.resize((blur_width, blur_height)).filter(ImageFilter.GaussianBlur(radius=300))
    blurimage = blurimage.crop( (0,0,image_canvas_width,image_canvas_height) )
    main_x_offset = int((image_canvas_width-main_width)/2)
    main_y_offset = int(((image_canvas_height)-main_height)/2)

    new_im.putdata( blurimage.getdata() )
    new_im.paste( mainimage, (main_x_offset, main_y_offset, main_x_offset+main_width, main_y_offset+main_height) )
    # new_im.paste( logoimage, (0,image_canvas_height,logo_width,full_height) )

    # Draw name
    # tw, th = get_text_dimensions(cname, font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 90))
    # draw = ImageDraw.Draw(new_im)
    #
    # draw.text((main_x_offset+main_width-(tw+th*0.5)-offset+2, int((image_canvas_height-(image_canvas_height-main_height)/2)-th*1.5)+2) ,cname, fill='#000000',font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 90))
    # draw.text((main_x_offset+main_width-(tw+th*0.5)-offset, int((image_canvas_height-(image_canvas_height-main_height)/2)-th*1.5)) ,cname, fill='#FFFFFF',font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 90))

    try:
        new_im = convert_to_srgb(new_im)
    except Exception as e:
        print('fail convert',e)
        new_im = new_im

    Path(os.path.join(social_media_dir,str(subheader[:-5]),str(name))).mkdir(parents=True, exist_ok=True)
    if not prize:
        p = os.path.join(social_media_dir,str(subheader[:-5]),str(name),str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-insta-sq.jpg')
        new_im.save(p, icc_profile=new_im.info.get('icc_profile'))
    else:
        p = os.path.join(social_media_dir,str(subheader[:-5]),str(name),'_'+str(prize)+'_'+str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-insta-sq.jpg')
        new_im.save(p, icc_profile=new_im.info.get('icc_profile'))

    write_xmp(p, data)

    #
    #
    # Build insta image 5x4
    # Build main image
    #
    #

    full_height = longedge
    full_width = int(longedge*4/5)

    scale_factor = (longedge/2000)

    # logo_height = int(master_logo_height*scale_factor)
    # logo_width = int(master_logo_width*scale_factor)
    # logoimage = masterlogoimage.resize((logo_width,logo_height))

    image_canvas_height =full_height
    image_canvas_width = full_width

    if main_width > main_height:
        main_height = int((image_canvas_width / main_width) * main_height)
        main_width = image_canvas_width
    else:
        main_width = int(((image_canvas_height) / main_height) * main_width)
        main_height = image_canvas_height

    new_im = Image.new(mode="RGB", size=(full_width,full_height), color='WHITE')
    mainimage = mainimage.resize((main_width, main_height))

    # now add blur background to mainimage
    if main_width<image_canvas_width:
        blur_width = image_canvas_width
        blur_height = int( (image_canvas_width/main_width) * main_height )
    elif main_height<image_canvas_height:
        blur_height = image_canvas_height
        blur_width = int( (image_canvas_width/main_height) * main_width )
    else:
        blur_width = main_width
        blur_height = main_height

    blurimage = mainimage.resize((blur_width, blur_height)).filter(ImageFilter.GaussianBlur(radius=300))
    blurimage = blurimage.crop( (0,0,image_canvas_width,image_canvas_height) )
    main_x_offset = int((image_canvas_width-main_width)/2)
    main_y_offset = int(((image_canvas_height)-main_height)/2)

    new_im.putdata( blurimage.getdata() )
    new_im.paste( mainimage, (main_x_offset, main_y_offset, main_x_offset+main_width, main_y_offset+main_height) )
    # new_im.paste( logoimage,(0,image_canvas_height,logo_width,full_height))

    # Draw name
    # tw, th = get_text_dimensions(cname, font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 70))
    # draw = ImageDraw.Draw(new_im)

    # draw.text((main_x_offset+main_width-(tw+th*0.5)-offset+2, int((image_canvas_height-(image_canvas_height-main_height)/2)-th*1.5)+2) ,cname, fill='#000000',font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 70))
    # draw.text((main_x_offset+main_width-(tw+th*0.5)-offset, int((image_canvas_height-(image_canvas_height-main_height)/2)-th*1.5)) ,cname, fill='#FFFFFF',font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 70))

    try:
        new_im = convert_to_srgb(new_im)
    except:
        print('fail convert')
        new_im = new_im

    Path(os.path.join(social_media_dir,str(subheader[:-5]),str(name))).mkdir(parents=True, exist_ok=True)
    # new_im.save(os.path.join(social_media_dir,str(subheader[:-5]),str(name),str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-insta-45.jpg'))
    if not prize:
        p = os.path.join(social_media_dir,str(subheader[:-5]),str(name),str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-insta-45.jpg')
        new_im.save(p, icc_profile=new_im.info.get('icc_profile'))
    else:
        p = os.path.join(social_media_dir,str(subheader[:-5]),str(name),'_'+str(prize)+'_'+str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-insta-45.jpg')
        new_im.save(p, icc_profile=new_im.info.get('icc_profile'))
    write_xmp(p, data)

    #
    #
    # Build insta image 3x2
    # Build main image
    #
    #

    full_height = int(longedge*2/3)
    full_width = longedge

    scale_factor = (longedge/2000)

    # logo_height = int(master_logo_height*scale_factor)
    # logo_width = int(master_logo_width*scale_factor)
    # logoimage = masterlogoimage.resize((logo_width,logo_height))

    image_canvas_height =full_height
    image_canvas_width = full_width

    if main_width > main_height:
        main_height = int((image_canvas_width / main_width) * main_height)
        main_width = image_canvas_width
    else:
        main_width = int(((image_canvas_height) / main_height) * main_width)
        main_height = image_canvas_height

    new_im = Image.new(mode="RGB", size=(full_width,full_height), color='WHITE')
    mainimage = mainimage.resize((main_width, main_height))

    # now add blur background to mainimage
    if main_width<image_canvas_width:
        blur_width = image_canvas_width
        blur_height = int( (image_canvas_width/main_width) * main_height )
    elif main_height<image_canvas_height:
        blur_height = image_canvas_height
        blur_width = int( (image_canvas_width/main_height) * main_width )
    else:
        blur_width = main_width
        blur_height = main_height

    blurimage = mainimage.resize((blur_width, blur_height)).filter(ImageFilter.GaussianBlur(radius=300))
    blurimage = blurimage.crop( (0,0,image_canvas_width,image_canvas_height) )
    main_x_offset = int((image_canvas_width-main_width)/2)
    main_y_offset = int(((image_canvas_height)-main_height)/2)

    new_im.putdata( blurimage.getdata() )
    new_im.paste( mainimage, (main_x_offset, main_y_offset, main_x_offset+main_width, main_y_offset+main_height) )


    # new_im.paste( logoimage,(0,image_canvas_height,logo_width,full_height))

    # Draw name
    # tw, th = get_text_dimensions(cname, font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 70))
    # draw = ImageDraw.Draw(new_im)

    # draw.text((main_x_offset+main_width-(tw+th*0.5)-offset+2, int((image_canvas_height-(image_canvas_height-main_height)/2)-th*1.5)+2) ,cname, fill='#000000',font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 70))
    # draw.text((main_x_offset+main_width-(tw+th*0.5)-offset, int((image_canvas_height-(image_canvas_height-main_height)/2)-th*1.5)) ,cname, fill='#FFFFFF',font=ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 70))

    try:
        new_im = convert_to_srgb(new_im)
    except:
        print('fail convert')
        new_im = new_im

    Path(os.path.join(social_media_dir,str(subheader[:-5]),str(name))).mkdir(parents=True, exist_ok=True)
    # new_im.save(os.path.join(social_media_dir,str(subheader[:-5]),str(name),str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-insta-32.jpg'))
    if not prize:
        p = os.path.join(social_media_dir,str(subheader[:-5]),str(name),str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-insta-32.jpg')
        new_im.save(p, icc_profile=new_im.info.get('icc_profile'))
    else:
        p = os.path.join(social_media_dir,str(subheader[:-5]),str(name),'_'+str(prize)+'_'+str(user_id)+'_'+str(name).replace(' ','_')+'_'+str(entry_id)+'-insta-32.jpg')
        new_im.save(p, icc_profile=new_im.info.get('icc_profile'))

    write_xmp(p, data)

    return

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

#################################################################


if __name__ == "__main__":

    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", help="reference directory", default=os.getcwd())
    parser.add_argument("--image_source_directory_secondary", help="secondary image source directory", default='../NLPA-Images-WithJudgeScoress')
    parser.add_argument("--image_source_directory_primary", help="primary image source directory", default='NLPA-2023-judged')
    parser.add_argument("--fullcsv", help="master data csv", default='nlpa_combined_entries.csv')
    parser.add_argument("--primarycsv", help="everything with judge data title caption raw etc", default='jb_listview_primary.csv')
    parser.add_argument("--secondarycsv", help="secondary with judge data title caption etc", default='jb_listview_secondary.csv')
    parser.add_argument("--prefinalscsv", help="firs live finals without judge data, just ids", default='jb_listview_prefinals.csv')
    parser.add_argument("--finalscsv", help="finals without judge data, just ids", default='jb_listview_finals.csv')
    parser.add_argument("--rawcheckingcsv", help="exported with colour labels for raw checking", default='jb_listview_PostCompetitionRawChecking.csv')

    parser.add_argument("--config", help="yaml config file", default="config.yaml")

    parser.add_argument("--make_entries", help="make entry certs", default=False)
    parser.add_argument("--make_portfolios", help="make portfolio certs", default=False)
    parser.add_argument("--make_projects", help="make project certs", default=False)

    parser.add_argument("--cert_folder", help="folder for certificates", default='photo_certs')
    parser.add_argument("--certs_csv", help="folder for certificate spreadsheet", default='certs.csv')
    parser.add_argument("--portfolio_csv", help="folder for portfolio final live judging", default='jb_listview_portfolio_finals.csv')
    parser.add_argument("--skipexisting", help="skip already existing certs", default=False)

    parser.add_argument("--shorttestrun", help="only run the first 20 from each csv", default=False)
    parser.add_argument("--cachedir", help="cache for generated images", default='photo_certs_cache')
    parser.add_argument("--make_socialmedia", help="make social media files", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--dryrun", help="don't process images", action=argparse.BooleanOptionalAction, default=False)


    # parser.add_argument("--judge", help="judge specific output", default=None)
    # parser.add_argument("--anon", help="make anonymous", default=False)
    # parser.add_argument("--raws", help="process raw files", default=False)
    # parser.add_argument("--rawcheckcsv", help="use csv backup of raw labels", default=False)
    # parser.add_argument("--dryrun", help="don't process images", default=False)
    # parser.add_argument("--target_base", help="base target directory name", default='NLPA-2022-judged-new2')
    # parser.add_argument("--filter_projects", help="list of project category names", default=False)



    args = parser.parse_args()
    config = args.config





    shorttestrun = args.shorttestrun

    cachedir = args.cachedir
    dryrun = args.dryrun

    with open(config) as f:
         yaml_data = yaml.safe_load(f)

    yaml_args = yaml_data['args']

    # portfolio_module = yaml_args.get('portfolio_module')
    # portfolio = __import__(portfolio_module)
    # port_ids = portfolio.port_ids
    # scores_dict = portfolio.scores_dict


    year = yaml_args['year']

    projects_csv = yaml_args['projects_csv']
    full_csv = yaml_args.get('fullcsv', args.fullcsv)
    primary_csv = yaml_args.get('primarycsv', args.primarycsv)
    secondary_csv = yaml_args.get('secondarycsv', args.secondarycsv)
    prefinals_csv = yaml_args.get('prefinalscsv', args.prefinalscsv)
    finals_csv = yaml_args.get('finalscsv', args.finalscsv)
    rawchecking_csv = yaml_args.get('rawcheckingcsv', args.rawcheckingcsv)
    portfolio_csv = yaml_args.get('portfolio_csv', args.portfolio_csv)

    social_media_dir = yaml_args.get('social_media_dir')


    cert_folder = yaml_args.get('cert_folder', args.cert_folder)
    certs_csv = yaml_args.get('certs_csv', args.certs_csv)

    image_source_directory_secondary = yaml_args.get('image_source_directory_secondary', args.image_source_directory_secondary)
    image_source_directory_primary = yaml_args.get('image_source_directory_primary', args.image_source_directory_primary)


    missing_ids = []



    make_projects = yaml_args.get('make_projects', args.make_projects)
    make_portfolios = yaml_args.get('make_portfolios', args.make_portfolios)
    make_entries = yaml_args.get('make_entries', args.make_entries)
    make_socialmedia = yaml_args.get('make_socialmedia', args.make_socialmedia)





    skipexisting = args.skipexisting


    judge_names = yaml_data['judges']
    caption = yaml_data['caption']

    caption_sections = re.split(r'(^[A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]) ([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).([A-Z])([0-9]).*', caption, flags=re.MULTILINE)

    caption_sections = caption_sections[1:-1]

    judge_initials = []

    for n in range(8):
        judge_initials.append( caption_sections[n*2] )
    judge_initial_position = ''.join(judge_initials[:5])


    cert_data = {}

    cat_winners_new = yaml_data['cat_winners']

    # fix new format of config.yaml
    cat_winners = {}

    for k, v in cat_winners_new.items():

        for K,V in v.items():
            if "Photograph" in V:
                cat_winners['overall'] = {}
                cat_winners['overall'][K] = V
            else:
                if k not in cat_winners:
                    cat_winners[k] = {}
                cat_winners[k][K] = V



    all_cat_winners = {}

    for v in cat_winners.values():
        all_cat_winners.update(v)

    special_cat_winners_new = yaml_data['special_winners']

    # Fix new format
    special_cat_winners = {}
    for k, v in special_cat_winners_new.items():
        for K,V in v.items():
            if k not in special_cat_winners:
                special_cat_winners[k] = {}
            special_cat_winners[k][K] = V

    all_special_winners = {}
    for cat, winners in special_cat_winners.items():
        for id, position in winners.items():
            all_special_winners[id] = (cat, position)



    final_ids_new = yaml_data['poty']

    # fix
    final_ids = {}
    for k,v in final_ids_new.items():
        final_ids[k] = v['id']




    final_voting = []
    for eid, entry in final_ids.items():
        final_voting.append(eid)

    project_final_ids_new = yaml_data['projects']
    # fix
    project_final_ids = {}
    for k,v in project_final_ids_new.items():
        project_final_ids[k] = v['id']

    # print(project_final_ids)

    def get_user_and_entry_from_filename(f):
        if '__' in f:
            token = '__'
        else:
            token = '_'
        return [int(x) for x in f[:-4].rsplit(token, maxsplit=2)[1:]]


    def get_photo_from_row(r, caption_sections, is_secondary):
        category = r['Folder']
        filename = r['File,name']
        if not filename.endswith('jpg'):
            return None, None, None
        caption = r['Caption']
        title = r['Title']
        label = r['Color,Name']


        if filename == '00_project_description.jpg':
            return None, None, None

        user_id, entry_id = get_user_and_entry_from_filename(r['File,name'])

        if is_secondary:
            j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_secondary_caption(caption, title, caption_sections)
        else:
            j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_caption(caption, title, caption_sections)

        photo = {
          'category': category,
          'filename': filename,
          'caption': caption,
          'title': title,
          'label': label,
          'is_secondary': is_secondary,
          'is_finals': False,
          'is_prefinals': False,
          'user_id': user_id,
          'entry_id': entry_id,
        }

        return user_id, entry_id, photo



    category_lookup = yaml_data['category_lookup']
    primary_dir = yaml_data['primary']
    secondary_dir = yaml_data['secondary']


    df = pd.read_csv(full_csv)
    entry_by_user_id = {}
    entry_by_entry_id = {}
    for i in range(len(df)):
        r = df.loc[i]
        id = r['id']
        entry_id = r['entry_id']
        if id in entry_by_user_id:
            entry_by_user_id[id].append(r)
        else:
            entry_by_user_id[id] = [r]



        entry_by_entry_id[entry_id] = r







    photos_by_user_id = {}
    photos_by_entry_id = {}

    # print('secondary')
    secondary_rows = pd.read_csv(secondary_csv,keep_default_na=False)

    len_secondary = len(secondary_rows)

    if shorttestrun:
        len_secondary = 30

    for i in range(len_secondary):
        r = secondary_rows.loc[i]
        user_id, entry_id, photo = get_photo_from_row(r, caption_sections, True)

        if not photo or photo['filename'].count('_') > 4:
            continue

        photos_by_entry_id[entry_id] = photo

        if user_id not in photos_by_user_id:
            photos_by_user_id[user_id] = {entry_id:photo}
        else:
            photos_by_user_id[user_id][entry_id] = photo


    ##### Need to combine the secondary scores with the primaries somehow!!!

    # print('primary')
    primary_rows = pd.read_csv(primary_csv,keep_default_na=False)
    len_primary = len(primary_rows)

    if shorttestrun:
        len_primary = 30


    for i in range(len_primary):
        r = primary_rows.loc[i]
        user_id, entry_id, photo = get_photo_from_row(r, caption_sections, False)



        if not photo or photo['filename'].count('_') > 4:
            continue

        photos_by_entry_id[entry_id] = photo

        if user_id not in photos_by_user_id:
            photos_by_user_id[user_id] = {entry_id:photo}
        else:
            photos_by_user_id[user_id][entry_id] = photo


    # print('prefinals')
    prefinals_rows = pd.read_csv(prefinals_csv,keep_default_na=False)


    if shorttestrun:
        start_prefinals = 10
        len_prefinals = 20
    else:
        start_prefinals = 0
        len_prefinals = len(prefinals_rows)

    for i in range(start_prefinals, start_prefinals+len_prefinals):
        r = prefinals_rows.loc[i]

        user_id, entry_id = get_user_and_entry_from_filename(r['File,name'])
        photo = photos_by_entry_id[entry_id]
        photo['is_prefinals'] = True

        if not photo or photo['filename'].count('_') > 4:
            continue

        photos_by_entry_id[entry_id] = photo

        if user_id not in photos_by_user_id:
            photos_by_user_id[user_id] = {entry_id:photo}
        else:
            photos_by_user_id[user_id][entry_id] = photo



    # print('finals')
    finals_rows = pd.read_csv(finals_csv,keep_default_na=False)


    if shorttestrun:
        start_finals = 10
        len_finals = 20
    else:
        start_finals = 0
        len_finals = len(finals_rows)

    for i in range(start_finals, start_finals+len_finals):
        r = finals_rows.loc[i]

        user_id, entry_id = get_user_and_entry_from_filename(r['File,name'])
        photo = photos_by_entry_id[entry_id]
        photo['is_finals'] = True

        if not photo or photo['filename'].count('_') > 4:
            continue

        photos_by_entry_id[entry_id] = photo

        if user_id not in photos_by_user_id:
            photos_by_user_id[user_id] = {entry_id:photo}
        else:
            photos_by_user_id[user_id][entry_id] = photo




    if make_projects or make_socialmedia:
    # if make_projects:
        # projects = pd.read_csv('projects_tweaked.csv',keep_default_na=False)
        projects = pd.read_csv(projects_csv,keep_default_na=False)

        count_project_by_stages = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }

        count_projectuser_by_stages = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }

        print('Building Projects')
        for i in range(len(projects)):
            # printProgressBar(i + 1, len(projects), prefix = 'Progress:', suffix = 'Complete', length = 80)
            r = projects.loc[i]
            batch = int(r['batch'])
            user_id = int(r['user_id'])
            livefinals = r['livefinals']
            secondary = r['secondround']
            semifinals = r['semifinals']
            shown = r['showntojudges']
            secondjudging = r['secondjudging']
            filename = r['filename']
            title = r['title']
            path = r['path']
            project_1 = str(entry_by_user_id[user_id][0]['project_title_one'])
            project_2 = str(entry_by_user_id[user_id][0]['project_title_two'])
            if batch == 1:
                project_title = project_1
            else:
                project_title = project_2








            j_scores = json.loads(r['j_scores'])
            o_scores = json.loads(r['o_scores'])
            j_score_data = json.loads(r['j_score_data'])
            o_score_data = json.loads(r['o_score_data'])

            if not shown:
                scores = o_scores.values()
            else:
                scores = j_scores.values()
            if project_final_ids.get("{}-{}".format(batch, user_id)) is not None:
                prize = project_final_ids.get("{}-{}".format(batch, user_id))
                suffix = '-{}'.format(prize).replace(' ','_').replace(',','_').lower()
            else:
                prize = None
                suffix = ''

            target_filename = "{}/{}/project-{}{}.jpg".format(cert_folder,r['user_id'], r['batch'], suffix)
            name = entry_by_user_id[r['user_id']][0]['name']
            subheader = project_title
            if livefinals:
                stage = 6
            elif semifinals:
                stage = 5
            elif secondary:
                stage = 4
            elif shown:
                stage = 3
            elif secondjudging:
                stage = 2
            else:
                stage = 1
            # print(user_id, shown, quarters, semifinals, finals, stage)
            if not dryrun:
                Path("{}/{}".format(cert_folder,int(r['user_id']))).mkdir(parents=True, exist_ok=True)


# need two image source directories - one for secondary and one for primary??

            # images = []
            # for n in [1,2,3,4,5]:
            #     images_folder = "../NLPA-Images-WithJudgeScores/Primary (grade all)/4 - Project/{}-{}-{}".format(n,r['batch'],r['user_id'])
            #     #print(images_folder)
            #     if os.path.isdir(images_folder):
            #         break
            #     images_folder = "../NLPA-Images-WithJudgeScores/Secondary (optional extras)/4 - Project/{}-{}-{}".format(n,r['batch'],r['user_id'])
            #     #print(images_folder)
            #     if os.path.isdir(images_folder):
            #         break
            # else:
            #     print('failed')
            #     sys.exit()



            images = []
            source = Path(image_source_directory_secondary)
            images_folder = source / secondary_dir / '4 - Project' / path
            if not os.path.exists(images_folder):
                images_folder = source / primary_dir / '4 - Project' / path




            for filename in os.listdir(images_folder):
                if filename != "00_project_description.jpg":
                    count_project_by_stages[stage] += 1
                    images.append( os.path.join(images_folder,filename) )
            user_id = int(r['user_id'])
            count_projectuser_by_stages[stage] += 1
            # adjust first round scores
            if stage == 1:
                scores_out = [s/1.7 for s in scores]
            else:
                scores_out = [s*0.85 for s in scores]

            if make_projects:
                data = build_cert(target_filename, images, scores_out, name, subheader, stage, False, prize, year, dryrun, cachedir)
                if user_id in cert_data:
                    cert_data[user_id].append( data )
                else:
                    cert_data[user_id] = [ data ]


            #
            # WE NEED SOME CODE IN HERE TO SPIT OUT SOCIAL MEDIA RESULTS FOR PROJECTS
            # WE SHOULD HAVE A SET OF IMAGES LIKE WE HAVE FOR THE BUILD_CERTIFICATE SECTION
            #
            if make_socialmedia:
                for image in images:
                    user_id, entry_id = get_user_and_entry_from_filename(image)
                    if not dryrun:
                        build_socialmedia('{}_{}'.format(batch,user_id), entry_id, entry_by_entry_id, image, scores, name, '{} {}'.format('Projects', year), stage, False, prize, year, cachedir, social_media_dir)




        print("projects")
        count = count_project_by_stages
        total = sum(count.values())
        print(total)

        for k in range(1,len(count)+1):
            v = count[k]

            print('{}: {}, {:.0f}%'.format(k,v,(v/total)*100))
        print('projects percentages')
        for k in range(1,len(count)+1):
            v = count[k]
            if k == 1:
                subtotal = total
            if k == 2:
                subtotal = sum([count[2], count[3], count[4], count[5], count[6]])
            if k == 3:
                subtotal = sum([count[3], count[4], count[5], count[6]])
            if k == 4:
                subtotal = sum([count[4], count[5], count[6]])
            if k == 5:
                subtotal = sum([count[5], count[6]])
            if k == 6:
                subtotal = sum([count[6]])
            print('{}: {}, {:.0f}%'.format(k,subtotal,(subtotal/total)*100))

        print("projects by user")
        print(count_projectuser_by_stages)
        count = count_projectuser_by_stages
        total = sum(count.values())

        for k in range(1,len(count)+1):
            v = count[k]

            print('{}: {}, {:.0f}%'.format(k,v,(v/total)*100))
        print('Projects by Photograph')
        pb = {}
        for k in range(1,len(count)+1):
            v = count[k]
            if k == 1:
                subtotal = total
            if k == 2:
                subtotal = sum([count[2], count[3], count[4], count[5], count[6]])
            if k == 3:
                subtotal = sum([count[3], count[4], count[5], count[6]])
            if k == 4:
                subtotal = sum([count[4], count[5], count[6]])
            if k == 5:
                subtotal = sum([count[5], count[6]])
            if k == 6:
                subtotal = sum([count[6]])
            print('{}: {}, {:.0f}%'.format(k,subtotal,(subtotal/total)*100))
            pb[k] = {'c': subtotal, 'p': (subtotal/total)*100 }
###### MAKE PORTFOLIOS ###############################################################
    if make_portfolios:

        for i, (entry_id, photo) in enumerate(photos_by_entry_id.items()):
            printProgressBar(i + 1, len(photos_by_entry_id.keys()), prefix = 'Progress:', suffix = 'Complete', length = 80)
            user_id = photo['user_id']
            category = photo['category']

            if category not in category_lookup.values():
                continue
            caption = photo['caption']
            title = photo['title']
            is_secondary = photo['is_secondary']
            is_prefinals = photo['is_prefinals']
            is_finals = photo['is_finals']
            rawcheck = photo.get('rawcheck', 'missing')
            filename = photo['filename']

            # CHECK MAIN WINNERS
            prize = all_cat_winners.get(entry_id)
            if prize is not None:
                suffix = '-{}-{}'.format(category[4:],prize).replace(' ','_')
                cat = category[4:]
            else:
                suffix = ''
                cat = category[4:]

            # CHECK SPECIAL WINNERS
            if all_cat_winners.get(entry_id) is None:
                cat, prize = all_special_winners.get(entry_id, (None, None))
                if prize is not None:
                    suffix = '-{}-{}'.format(cat.replace('/','_'), prize).replace(' ','_')
                else:
                    suffix = ''
                    cat = category[4:]

            if is_secondary:
                j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_secondary_caption(caption, title, caption_sections)
                o_score_data = score_var_calc_org(o_scores_list)
            else:
                j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_caption(caption, title, caption_sections)
                j_score_data = score_var_calc_judges(j_scores_list)
                o_score_data = score_var_calc_org(o_scores_list)



        ## Is this the finals portfolios?
        # jb_listview_portfolios_finals.csv

        count_portfolio_by_stages = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }

        #encoded_filename = base64.b64encode(filename[::-1][5:].encode('ascii')).decode('ascii')[:8]
        #anon_filename = '%s__%s__%s.jpg'%(directory,id,entry_id)
        #target_filename =  os.path.join(target_directory, anon_filename)

        pf_rows = pd.read_csv(portfolio_csv, keep_default_na=False)
        pf_in_finals_live = []
        if shorttestrun:
            start_pf = 10
            len_pf = 20
        else:
            start_pf = 0
            len_pf = len(pf_rows)

        for i in range(start_pf, start_pf+len_pf):
            r = pf_rows.loc[i]

            try:
                user_id, entry_id = get_user_and_entry_from_filename(r['File,name'])
            except ValueError:
                #print('problem with %s'%r['File,name'])
                continue
            if user_id not in pf_in_finals_live:
                pf_in_finals_live.append(user_id)



        high = 0
        low = 5
        count = {5:0, 4:0, 3:0, 2:0, 1:0, 6:0}


        port_average_vs_portfolio_out = []
        oscore_array = {}
        jscore_array = {}

        # build scores_dict by entry_id
        score_data_by_entry_id = {}
        for user_id, v in scores_dict.items():
            for entry_id, jscore in v['jscores'].items():
                score_data_by_entry_id[entry_id] = {
                                    'jscore': v['jscores'][entry_id],
                                    'oscore': v['oscores'][entry_id],
                                    'score': v['scores'][entry_id],
                                    'per_judge_scores': v['scoreset'][entry_id],
                                    }

        print('Building Portfolios')
        for i, (id, score) in enumerate(port_ids):
            # printProgressBar(i + 1, len(port_ids), prefix = 'Progress:', suffix = 'Complete', length = 80)

            scores = {}
            images = []
            subheader = "Combined Portfolio"










            if final_ids.get(int(id)) is not None:
                prize = final_ids.get(int(id))
                suffix = '-{}'.format(prize).replace("Photographer of the Year","combined_portfolio").replace(' ','_').replace(',','_').lower()
            else:
                prize = None
                suffix = ''
            target_filename = "{}/{}/combined-portfolio{}.jpg".format(cert_folder,int(id),suffix)
            score_array = {}
            if not dryrun:
                Path("{}/{}".format(cert_folder,int(id))).mkdir(parents=True, exist_ok=True)


            oscore_set = []
            jscore_set = []
            entry_count = 0



            # THIS IS GOING THROUGH ALL OF THE IMAGES


            for entry_id in scores_dict[str(id)]['items'].keys():
                entry_count += 1

                score_data = score_data_by_entry_id[entry_id]
                jscores = score_data['per_judge_scores']['j']['scores']
                oscores = score_data['per_judge_scores']['o']['scores']

                # print('jscores',jscores)
                # print('oscores', oscores)
                # if oscores[-1] == 0:
                #     oscores = oscores[0:3]
                #     oscores.append(3)
                #
                # if oscores[-1] > 3:
                #     oscores = oscores[0:3]
                #     oscores.append(3)



                oscore_set.append(oscores)
                jscore_set.append(jscores)

                # print('jscore_set',jscore_set)
                # print('oscore_set',oscore_set)

                if int(entry_id) not in photos_by_entry_id:
                    print('MISSING %s'%entry_id)
                    continue
                e = photos_by_entry_id[int(entry_id)]
                entry = entry_by_entry_id[int(entry_id)]
                name = entry['name']

                filename = e['filename']
                category = e['category']
                primary_dir = "Primary (grade all)"

                for cat in [v for v in category_lookup.values() if v[0] in ['1','2','3']]:
                    source = Path(image_source_directory_secondary)
                    f = source / secondary_dir / cat / filename
                    if os.path.isfile(f):
                        break
                    source = Path(image_source_directory_primary)
                    f = source / primary_dir / cat / filename
                    if os.path.isfile(f):
                        break


                # metadata = pyexiv2.ImageMetadata(f)
                # metadata.read()
                # caption = metadata['Xmp.dc.description'].value['x-default'][1:]

                try:
                    image = Image.open(f)
                except PIL.UnidentifiedImageError:
                    print('problem with ', f)
                    continue
                exifdata = image.getexif()
                caption = exifdata.get(270)
                title = None



                # if not caption or caption[1] == ' ':
                #     score_array[entry_id] = [0,0,0,0,0,0,0,0]
                # else:
                #     j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_caption(caption, title, caption_sections)
                #     score_array[entry_id] = j_scores_list
                images.append(f)



            if len(images) <6:
                continue

            oscore_avg = [sum(vals)/len(oscore_set) for vals in zip(*oscore_set)]
            jscore_avg = [sum(vals)/len(jscore_set) for vals in zip(*jscore_set)]

            # print("{}, ({})".format(name, id))
            #
            # print('raw o,len(o)')
            #
            # print(oscore_avg)
            # print(len(oscore_set))
            #
            # print('raw j,len(j)')
            #
            # print(jscore_avg)
            # print(len(jscore_set))

            if jscore_avg != [0.0,0.0,0.0,0.0,0.0]:
                jscore_avg_tuple = [
                    (0,jscore_avg[0]),
                    (1,jscore_avg[1]),
                    (2,jscore_avg[2]),
                    (3,jscore_avg[3]),
                    (4,jscore_avg[4]),
                ]

                # print('jscore_avg_tuple')
                # print(jscore_avg_tuple)
                osao = sorted(oscore_avg)
                jsao = sorted(jscore_avg_tuple, key=lambda tup: tup[1])


                if len(osao) == 0:
                    osao = oscore_avg = [0,0,0,0]

                if len(jsao) == 0:
                    jsao = jscore_avg = [0,0,0,0,0]

                # print('sorted o,j')
                # print(osao)
                # print(jsao)

                org_influence_factor = 0.2
                jscore_offset = 2.5
                jscore_scale = 2/5
                oif = org_influence_factor

                # print(jsao[0][1], len(jscore_set), osao[0], len(oscore_set))
                # print(( jsao[0][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[0]*len(oscore_set) ) /6)
                # print(( jsao[1][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[1]*len(oscore_set) ) /6)
                # print(( jsao[2][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[2]*len(oscore_set) ) /6)
                # print(( jsao[3][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[3]*len(oscore_set) ) /6)
                # print(( jsao[4][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[0]*len(oscore_set) ) /6)
                avg = {
                    jsao[0][0]: ( jsao[0][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[0]*len(oscore_set) ) /6,
                    jsao[1][0]: ( jsao[1][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[0]*len(oscore_set) ) /6,
                    jsao[2][0]: ( jsao[2][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[1]*len(oscore_set) ) /6,
                    jsao[3][0]: ( jsao[3][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[1]*len(oscore_set) ) /6,
                    jsao[4][0]: ( jsao[4][1]*len(jscore_set)*jscore_scale + len(jscore_set)*jscore_offset + oif*osao[2]*len(oscore_set) ) /6,
                }
                # print('combined_avg')
                # print(avg)


                avg_scores_out = [
                    avg[0],
                    avg[1],
                    avg[2],
                    avg[3],
                    avg[4],
                 ]
            else:
                # print('only o scores')
                avg_scores_out = [s/1.7 for s in oscore_avg]

            # print('final list')
            # print(avg_scores_out)

            # if osao.count(0) != 4 and len(oscore_set)>1:
            #     sys.exit()


            if int(id) in final_voting:
                stage = 6
            elif int(id) in pf_in_finals_live:
                stage = 5
            elif score >= 15:
                stage = 4
            elif score >= 12:
                stage = 3
            elif score >= 8:
                stage = 2
            else:
                stage = 1

            count[stage] += 1

            #### IF WE HAVE MIXED SCORES FROM JUDGES AND NOT FROM JUDGES, HOW DO WE WORK THINGS OUT?


            # port_average_vs_portfolio_out.append( (int(id),sum(avg_scores_out)/8, score, len(avg_scores_out) ) )



            user_id = int(id)

            jscore_array[int(id)] = jscore_avg
            oscore_array[int(id)] = oscore_avg
            # print(user_id, stage)
            # print('o',oscore_avg)
            # print('j',jscore_avg)

            if [0,0,0,0,0] in jscore_set:
                data = build_cert(target_filename, images, oscore_avg, name, subheader, stage, True, prize, year, dryrun, cachedir)
            else:
                data = build_cert(target_filename, images, jscore_avg, name, subheader, stage, True, prize, year, dryrun, cachedir)



            #
            # WE NEED SOME CODE IN HERE TO SPIT OUT SOCIAL MEDIA RESULTS FOR PORTFOLIO
            #
            if user_id in cert_data:
                cert_data[user_id].append( data )
            else:
                cert_data[user_id] = [ data ]


        # print('Final count of portfolios and stages')
        # print(count)
        # print('proportion of total')

        total = sum(count.values())

        for k in range(1,len(count)+1):
            v = count[k]

        print('accumulating proportion of total')
        wb = {}
        for k in range(1,len(count)+1):
            v = count[k]
            if k == 1:
                subtotal = total
            if k == 2:
                subtotal = sum([count[2], count[3], count[4], count[5]])
            if k == 3:
                subtotal = sum([count[3], count[4], count[5]])
            if k == 4:
                subtotal = sum([count[4], count[5]])
            if k == 5:
                subtotal = sum([count[5]])
            if total != 0:
                print('{}: {}, {:.0f}%'.format(k,subtotal,(subtotal/total)*100))
                wb[k] = {'c': subtotal, 'p': (subtotal / total) * 100}
            else:
                print('{}: {}, {:.0f}%'.format(k,subtotal,0))
                wb[k] = {'c': subtotal, 'p': 0}

        ss = sorted(port_average_vs_portfolio_out, key=lambda tup: tup[1])
        for t in ss:
            print("{0:}, {1:.2f}".format(t[0],t[1]*15,t[2], t[3]))

    if make_entries or make_socialmedia:



        count_by_stages = {
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0,
        }









        print('Building Photos from all main categories', len(photos_by_entry_id.keys()))
        for i, (entry_id, photo) in enumerate(photos_by_entry_id.items()):
            # printProgressBar(i + 1, len(photos_by_entry_id.keys()), prefix = 'Progress:', suffix = 'Complete', length = 80)
            user_id = photo['user_id']
            category = photo['category']

            if category not in category_lookup.values():
                continue
            caption = photo['caption']
            title = photo['title']
            is_secondary = photo['is_secondary']
            is_prefinals = photo['is_prefinals']
            is_finals = photo['is_finals']
            rawcheck = photo.get('rawcheck', 'missing')
            filename = photo['filename']





            # CHECK MAIN WINNERS
            prize = all_cat_winners.get(entry_id)
            if prize is not None:
                suffix = '-{}-{}'.format(category[4:],prize).replace(' ','_')
                cat = category[4:]
            else:
                suffix = ''
                cat = category[4:]

            # CHECK SPECIAL WINNERS
            if all_cat_winners.get(entry_id) is None:
                cat, prize = all_special_winners.get(entry_id, (None, None))
                if prize is not None:
                    suffix = '-{}-{}'.format(cat.replace('/','_'), prize).replace(' ','_')
                else:
                    suffix = ''
                    cat = category[4:]



            target_path = Path(cert_folder) / str(user_id)
            if not dryrun:
                target_path.mkdir(parents=True, exist_ok=True)
            target_filename = target_path / "{}{}.jpg".format(entry_id, suffix)

            #print(target_filename)
            if os.path.isfile(target_filename) and skipexisting:
                continue




            # GET TO THIS POINT AND WORK OUT SCORES!!!
            name = entry_by_user_id[user_id][0]['name']

            if is_secondary:
                j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_secondary_caption(caption, title, caption_sections)

                o_score_data = score_var_calc_org(o_scores_list)


            else:
                j_scores, o_scores, j_scores_list, o_scores_list, mean_score, raw_score = process_caption(caption, title, caption_sections)

                #tweak_rajesh(o_scores_list)

                j_score_data = score_var_calc_judges(j_scores_list)
                o_score_data = score_var_calc_org(o_scores_list)

            if is_secondary:
                stage = 1
                if o_score_data['raw_mean'] >= 2.5:
                    stage = 2
            else:
                stage = 3

                if 4 in j_scores_list or 5 in j_scores_list:
                    stage = 4
                if is_prefinals:
                    stage = 5
                if is_finals:
                    stage = 6



            count_by_stages[stage] += 1

            # make user folder

            primary_dir = "Primary (grade all)"

            if is_secondary:
                scores = o_scores_list
                source = Path(image_source_directory_secondary)

                f = source / primary_dir / category / filename
                if not os.path.isfile(f):
                    f = source / secondary_dir / category / filename

            else:
                scores = j_scores_list
                source = Path(image_source_directory_primary)

                f = source / primary_dir / category / filename

                if make_socialmedia:
                    build_socialmedia(user_id, entry_id, entry_by_entry_id, f, scores, name, '{} {}'.format(cat, year), stage, False, prize, year, cachedir, social_media_dir)






            if make_entries:
                try:
                    data = build_cert(target_filename, [f], scores, name, cat, stage, False, prize, year, dryrun, cachedir)
                except Exception as e:
                    print(e)
                    print(user_id, entry_id)
                    print(f,scores,name)

                if user_id in cert_data:
                    cert_data[user_id].append( data )
                else:
                    cert_data[user_id] = [ data ]

        print("How many photos ended in each stage")
        count = count_by_stages
        total = sum(count.values())

        for k in range(1,len(count)+1):
            v = count[k]
            print('{}: {}, {:.0f}%'.format(k, v, (v / total) * 100))


        eb = {}
        print('How many total photos in each stage (accumulating)')
        for k in range(1,len(count)+1):
            v = count[k]
            if k == 1:
                subtotal = total
            if k == 2:
                subtotal = sum([count[2], count[3], count[4], count[5]])
            if k == 3:
                subtotal = sum([count[3], count[4], count[5]])
            if k == 4:
                subtotal = sum([count[4], count[5]])
            if k == 5:
                subtotal = sum([count[5]])
            eb[k] = {'c': subtotal, 'p': (subtotal / total) * 100}


    certificates_labels = f"""
    if is_project:
        stage_text = {{}}
        stage_text[1] = "1. Pre-Judging ({pb[1]['c']} - {pb[1]['p']:.0f}%)"
        stage_text[2] = "2. Main Judging  ({pb[2]['c']} - {pb[2]['p']:.0f}%)"
        stage_text[3] = "3. Second Round  ({pb[3]['c']} - {pb[3]['p']:.0f}%)"
        stage_text[4] = "4. Pre-Finals ({pb[4]['c']} - {pb[4]['p']:.0f}%)"
        stage_text[5] = "5. Final Voting ({pb[5]['c']} - {pb[5]['p']:.1f}%)"
        stage_text[6] = "5. Live Voting ({pb[6]['c']} - {pb[6]['p']:.1f}%)"


    elif is_portfolio:
        stage_text = {{}}
        stage_text[1] = "1. First Judging ({wb[1]['c']} - {wb[1]['p']:.0f}%)"
        stage_text[2] = "2. Second Judging ({wb[2]['c']} - {wb[2]['p']:.0f}%)"
        stage_text[3] = "3. Main Judging ({wb[3]['c']} - {wb[3]['p']:.0f}%)"
        stage_text[4] = "4. Pre-Finals ({wb[4]['c']} - {wb[4]['p']:.0f}%)"
        stage_text[5] = "5. Final Live Judging ({wb[5]['c']} - {wb[5]['p']:.1f}%)"
        stage_text[6] = "6. Final Voting ({wb[6]['c']} - {wb[6]['p']:.1f}%)"

    else:

        stage_text = {{}}
        stage_text[1] = "1. First Pre-Judging ({eb[1]['c']} - {eb[1]['p']:.0f}%)"
        stage_text[2] = "2. Second Pre-Judging ({eb[2]['c']} - {eb[2]['p']:.0f}%)"
        stage_text[3] = "3. Main Judging ({eb[3]['c']} - {eb[3]['p']:.0f}%)"
        stage_text[4] = "4. Pre-Finals ({eb[4]['c']} - {eb[4]['p']:.0f}%)"
        stage_text[5] = "5. Final Live Judging ({eb[5]['c']} - {eb[5]['p']:.1f}%)"
        stage_text[6] = "6. Final Voting ({eb[6]['c']} - {eb[6]['p']:.1f}%)"
"""

    print('#'*30)
    print(certificates_labels)
    print('#'*30)



    with open(certs_csv, mode='w') as p:
        writer = csv.writer(p, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
                'id',
                'target_filename',
                'name',
                'subheader',
                'stage_text',
                'prize',
                'type',
                ])

        for user_id, certs in cert_data.items():
            for C in certs:
                writer.writerow([
                user_id,
                C.get('target_filename'),
                C.get('name'),
                C.get('subheader'),
                C.get('stage_text'),
                C.get('prize'),
                C.get('type'),
                ])
