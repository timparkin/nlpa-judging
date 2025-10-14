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
from pprint import pprint

MAKE_ANONYMOUS = False

# This can be used just to extract raws in a list of entry ids
try_raw_again = """""".splitlines()
# try_raw_again = """65909
# 53578
# 53586
# 59362"""
ONLANDSCAPE = False

GET_TOP_SCORES = False

inbookids_pages = """Name	Status	Page
Gary Ward__740__54732.jpg	OK	111
Lizzie Shepherd__293__61817.jpg	OK	65
gillian dayton__6046__60179.jpg	OK	216
Kristin Weinhold__2872__64094.jpg	OK	90
Jan Erik Waider__3411__62502.jpg	OK	98
Christian Wayne__1632__54008.jpg	OK	195
Daniel Martin__5934__56150.jpg	OK	71
Margy Kuntz__2722__63996.jpg	OK	205
Jeroen Van Nieuwenhove__2972__58113.jpg	OK	59
Johannes Kowalewski__313__59488.jpg	OK	80
Joel Tapernoux__5964__57349.jpg	OK	199
Dylan Nardini__1315__65561.jpg	OK	63
andrea sanchini__3251__55129.jpg	OK	70
Duncan MacArthur__2711__65362.jpg	OK	60
Jeremy Hansen__1715__58818.jpg	OK	88
Anton Gorlin__143__59217.jpg	OK	206
Michael Schertzberg__2713__63191.jpg	OK	82
Chuck Robinson__5810__63473.jpg	OK	69
Shumon Saito__3467__60970.jpg	OK	87
Sarfraz Durrani__5944__56829.jpg	OK	58
Bryan Mitchell__5892__55354.jpg	OK	83
Tobias Richter__810__62092.jpg	OK	217
Markus Schoch__4124__57296.jpg	OK	198
Rich Brooks__5825__54167.jpg	OK	99
Brian Venua__1951__65860.jpg	OK	207
John Ealing__1455__65301.jpg	OK	62
Mieke Boynton__359__57993.jpg	OK	81
Léo de Graaff__4387__62899.jpg	OK	101
Nigel Halliwell__264__56283.jpg	OK	110
Mark Hetherington__1829__54849.jpg	OK	97
Rupert Kogler__6187__63312.jpg	OK	100
Paul Lichte__5898__59958.jpg	OK	93
Pete Hyde__146__59001.jpg	OK	109
Julie Fletcher__5730__53429.jpg	OK	92
Ádám Fáth__838__65739.jpg	OK	108
Vlad Paulet__4694__65392.jpg	OK	115
Daniel Ward__409__54318.jpg	OK	113
Jeannet van der Knijff__3448__56498.jpg	OK	117
Sally Mason__4391__63109.jpg	OK	116
Rick Bowden__297__58185.jpg	OK	228
marek biegalski__87__58075.jpg	OK	114
OwensLakeMudcracks20230421_07191306_002.jpg	OK	220
Sho Hoshino__ciwywofi__1709__33826-fix_002.jpg	OK	220
Charlotte-Gibb-Portrait-black-and-white.jpeg	OK	220
image_6483441-6.jpeg	OK	222
Adam Gibbs__tzmbbzkk__2998__27329.jpg	OK	221
Tiago Mateus__aowmaspf__3628__35095.jpg	OK	221
Theo portrait 1000px.jpeg	OK	223
NLPA Matriarch RKJ09121.jpg	OK	227
NLPA Rime Ice RKJ02507.jpg	OK	227
an-teallach-snow-1.jpeg	OK	226
Charlotte Gibb_Portal-1800px-300-dpi.jpeg	OK	73
DSC5227cSQUARE-bnw-copy.jpeg	OK	219
hidden-senja-sunset.jpeg	OK	226
andymynmfrd.jpg	OK	221
Peter Dyndiuk__ctsyhtya__96__31422.jpg	OK	221
stac-pollaidh-autumn-view-from-cul-mor.jpeg	OK	226
Resilience.jpeg	OK	73
NLPA Burning Ashes  RKJ04251.jpg	OK	227
alex-nail-portrait.jpg	OK	226
Snowstorm in Crayon_003.jpeg	OK	219
FilmRolls_EricBennett_NLPA_V3.jpeg	OK	219
Charlotte Gibb-Last-Color.jpeg	OK	72
thefagradalsfjallfires-nlpa-5.jpg	OK	222
Josh Krasner__1373__64135.jpg	OK	1
Woodland-Logo-Black_CBP022771.pdf	OK	4
uffuzcbe__2745__38248_DJI_0357_xI9Gm4B-RAW-Edit.jpg	OK	222
winners-2.jpg	OK	119
voting.jpg	OK	118
MattRedfern_GoghWithTheFLow_NLPA.jpg	OK	222
20221218-_DSC1120冬物語.jpg	OK	219
Snowstorm in Crayon_003.jpeg	OK	223
Snowstorm in Crayon_002.jpeg	OK	220
8_002.jpg	OK	223
Uten_navn_Panoramax-1_002.jpg	OK	223
matt-logo-podcast.jpg	OK	4
headshot_1.jpg	OK	227
timparkin-108.jpg	OK	224
headshot.jpg	OK	225
tim2.jpeg	OK	224
tim6.jpeg	OK	224
Natural-Landscape-Awards-XtraLrg-Logo-Color-4000_002-logo_002.jpg	OK	4
extended-edition.jpg	OK	218
tim4.jpeg	OK	224
Natural-Landscape-Awards-XtraLrg-Logo-Color-4000_002-logo_001.jpg	OK	3
tim8.jpeg	OK	224
tim7.jpeg	OK	224
Torsten Pull__1704__61125.jpg	OK	182
Robert Birkby__3445__55893.jpg	OK	150
Louis Ouimet__3526__63587.jpg	OK	162
John Meragias__3622__55715.jpg	OK	163
ray Cao__1824__55961.jpg	OK	147
Subhasish Dutta__1716__59191.jpg	OK	179
Philipp Jakesch__97__57452.jpg	OK	149
Patrick Krohn__1482__58639.jpg	OK	190
Richard Tonge__6079__60694.jpg	OK	183
Magnus Reneflot__2625__60543.jpg	OK	130
Lizzie Shepherd__293__61820.jpg	OK	148
Magnus Reneflot__2625__60507.jpg	OK	133
Spencer Cox__2745__54962.jpg	OK	180
Alexander Miller__2015__55883.jpg	OK	161
Prajit Ravindran__428__61051.jpg	OK	164
Philip Williams__6088__63446.jpg	OK	156
Doug Hammer__2948__55742.jpg	OK	181
Magnus Reneflot__2625__60550.jpg	OK	189
Xavier Lequarre__3559__60578.jpg	OK	203
Mathias Libor__434__56949.jpg	OK	201
Anton Gorlin__143__56761.jpg	OK	191
Joshua Cripps__1052__58919.jpg	OK	204
Richard Doak__3650__63157.jpg	OK	212
Christopher Rutter__5979__58281.jpg	OK	193
Andrea Lazzarini__1310__65250.jpg	OK	210
Jack Krohn__1935__65811.jpg	OK	192
Franka Gabler__787__60086.jpg	OK	209
Kenny Muir__379__57958.jpg	OK	208
Grégoire Pansu__6197__64429.jpg	OK	202
Grégoire Pansu__6197__64433.jpg	OK	200
Rupert Kogler__6187__63311.jpg	OK	171
Jason Pettit__75__56093.jpg	OK	174
James Wade__5850__61493.jpg	OK	176
David Pedreira__6042__65329.jpg	OK	211
Vojtech Schmidt__6113__61790.jpg	OK	170
Lawrence Pallant__357__56681.jpg	OK	215
Ryunosuke Imamura__5873__59175.jpg	OK	214
Paul Hoelen__1413__64753.jpg	OK	175
Pal Hermansen__3756__59066.jpg	OK	172
Hunter Page__4258__59181.jpg	OK	165
Lukáš Veselý__3652__60358.jpg	OK	140
Cameron Wilcox__1717__57759.jpg	OK	153
Nelson Lutz__1105__54376.jpg	OK	177
Justin Leveillee__2645__62140.jpg	OK	167
Jochen Bongaerts__4568__61273.jpg	OK	188
Sho Hoshino__1709__55014.jpg	OK	173
Alexander Jones__1059__64650.jpg	OK	169
Lucie Averill__305__61299.jpg	OK	160
Crystal May__4359__59388.jpg	OK	154
gary silvey__2417__54392.jpg	OK	166
Joe Rainbow__60__62020.jpg	OK	197
Franka Gabler__787__60096.jpg	OK	184
Kazuki Sugiyama__3592__62605.jpg	OK	185
David Southern__98__57929.jpg	OK	159
Mário Cunha__559__56653.jpg	OK	146
Louis Ouimet__3526__63586.jpg	OK	186
Jeroen Van Nieuwenhove__2972__58117.jpg	OK	178
Peter Coskun__2832__58809.jpg	OK	168
Edward McGuirk__298__56578.jpg	OK	196
Yuya Tamura__4618__64536.jpg	OK	158
romain barats__5995__58193.jpg	OK	155
Axel Azni__1507__61777.jpg	OK	141
Steve Cozad__713__55136.jpg	OK	187
Rebecca Simrose__3085__53102.jpg	OK	145
Oliver Bunting__5941__58598.jpg	OK	142
Jason Schultz__4351__63830.jpg	OK	144
Hanneke Van Camp__3511__61092.jpg	OK	37
85206__4360__60258.jpg	OK	14
Feli Hansen__403__58982.jpg	OK	43
Hanneke Van Camp__3511__61084.jpg	OK	38
Feli Hansen__403__58977.jpg	OK	42
Feli Hansen__403__58984.jpg	OK	40
Margrit Schwarz__3690__65632.jpg	OK	7
15206__4360__60251.jpg	OK	15
49785__5815__58794.jpg	OK	21
54045__5815__54045.jpg	OK	20
65206__4360__60256.jpg	OK	10
17585__670__58571.jpg	OK	24
35206__4360__60253.jpg	OK	13
Hanneke Van Camp__3511__61091.jpg	OK	36
Hanneke Van Camp__3511__61087.jpg	OK	39
06585__670__58560.jpg	OK	25
Hanneke Van Camp__3511__61088.jpg	OK	35
30685__5815__58603.jpg	OK	18
27585__670__58572.jpg	OK	26
Hanneke Van Camp__3511__61085.jpg	OK	34
40685__5815__58604.jpg	OK	19
Hanneke Van Camp__3511__61090.jpg	OK	32
Feli Hansen__403__58978.jpg	OK	45
45206__4360__60254.jpg	OK	11
36206__4360__60263.jpg	OK	12
Lindsay Southgate__5859__55045.jpg	OK	2
Theo Bosboom__235__59551.jpg	OK	46
祐也 若松__5916__61003.jpg	OK	79
Theo Bosboom__235__59555.jpg	OK	48
Roger Kristiansen__1879__62732.jpg	OK	78
Theo Bosboom__235__59552.jpg	OK	51
Jude Dizon__1821__62740.jpg	OK	77
Samuel Markham__2198__55553.jpg	OK	54
Alex Pansier__5737__53123.jpg	OK	104
Theo Bosboom__235__59557.jpg	OK	50
Gunar Streu__2028__53855.jpg	OK	55
Theo Bosboom__235__59550.jpg	OK	49
Luis Vilariño__2509__53322.jpg	OK	52
Benjamin Maze__649__57008.jpg	OK	57
Vojtech Schmidt__6113__61786.jpg	OK	76
Feli Hansen__403__58986.jpg	OK	44
Ilan Shacham__972__54673.jpg	OK	102
Joshua Cripps__1052__58913.jpg	OK	56
Lukas Furlan__5815__58601.jpg	OK	107
Lukas Furlan__5815__54046.jpg	OK	105
Loren Root__1749__63226.jpg	OK	94
Scott Oller__1375__64157.jpg	OK	106
Joshua Wallace__6259__66282.jpg	OK	128
Joshua Wallace__6259__66283.jpg	OK	129
Ciaran Willmore__4335__62103.jpg	OK	66
Lukas Furlan__5815__54034.jpg	OK	122
Andrei Trocan__69__55324.jpg	OK	135
Magnus Reneflot__2625__60533.jpg	OK	132
Joshua Wallace__6259__66279.jpg	OK	126
Ross Davidson__3938__59594.jpg	OK	136
Lukas Furlan__5815__54032.jpg	OK	124
Scott Oller__1375__64172.jpg	OK	137
Jess Findlay__5747__60006.jpg	OK	139
Lukas Furlan__5815__54038.jpg	OK	123
Lukas Furlan__5815__54039.jpg	OK	125
Lukas Furlan__5815__54035.jpg	OK	120
Lukáš Veselý__3652__60354.jpg	OK	138
Joy Kachina Portrait-3.JPG	OK	28
YIHSUN CHOU__5739__54840.jpg	OK	112
Cider Gums Joy Kachina.JPG	OK	29
Matt Payne__9__53065.jpg	OK	225
LukasFurlan_5S8A3276.jpg	OK	16
MattJackisch_halo__DSC8441-Pano-Edit2.jpg	OK	27
Marlin Mills__6250__65640.jpg	OK	96
Living Gallery Joy Kachina.JPG	OK	8
Snowfall Cider Gums Joy Kachina.JPG	OK	29
Matt Payne__9__53105.jpg	OK	225
Pre Dawn Light Cider Gums Joy Kachina.JPG	OK	30
woosh.jpg	OK	225
Sunrise Mist Cider Gums Joy Kachina.JPG	OK	30
MattJackisch_fog.jpg	OK	22
Joy out in the Field Central Highlands.JPG	OK	31
Joe Rainbow__60__62023.jpg	OK	152
ALEXANDRE DESCHAUMES__1394__53463.jpg	OK	64
Johannes Kowalewski__313__59494.jpg	OK	86
james austrums__5889__59362.jpg	OK	151
Ben Wilkinson__6139__63348.jpg	OK	134
Baldea Victor__2881__57711.jpg	OK	68
Yuki Takizawa__2939__56715.jpg	OK	194
Andrew Baruffi__70__63518.jpg	OK	230
John Hardiman__1380__62656.jpg	OK	89
Gary Ward__740__54732.jpg	OK	84
Philipp Jakesch__97__57452.jpg	OK	61
Cameron Wilcox__1717__57768.jpg	OK	91
David Shaw - Jurassic World.jpg	OK	74""".splitlines()

inbookids = {}
for line in inbookids_pages:
    try:
        entry_id, page = line.split("\tOK\t")
        entry_id = entry_id.split('__')[2][:-4]
        if len(entry_id) != 5:
            continue
        inbookids[ entry_id ] = str(page).zfill(3)
    except (ValueError, IndexError):
        continue









missing_ids = [int(n) for n in """9999999999
""".splitlines()]

def shifttext(text, shift):
    a = ord('a')
    return ''.join(chr((ord(char) - a + int(shift)) % 26 + a) for char in text.lower())

skip_project = []
project_min_score = 24.0

# THESE ARE EXTRA IMAGES THAT DIDN"T SCORE A ONE STAR BUT I WANT TO INCLUDE
# include these images
extras_ids = []
# include these projects [(c,id),]
project_extras = []
# Only include these ids if not none [(c,id),]
finals_project_filter = None

skip_portfolio = []
portfolio_min_score = 18.0

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
    return text

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
        text = text.replace(value,str(key))
    return text

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

# THIS CODE IS ODD AS I COPIED THE FILES FROM THE ORIGINAL CACHE, THEN DOWNLOADED THE RAW FILES, ONLY TO REALISE I HADN'T REASSIGNED THE CATEGORIES.
# THE NEW_TARGET IS A DUPLICATE FOLDER WITH REMAPPED CATEGORIES - QUITE HANDY IN THE END AS I COULD WIPE IT AND THE RECREATION PROCESS WASN'T THAT EXPENSIVE.
# FOR THE NEXT RUN I NEED TO MAKE SURE I REMAP THE CATEGORIES FORST - TO FOR THE NEXT YEAR

#
# target_directory = where to pout downloads
# anon_prefix = filename prefix to randomise sorting
# directory = NOT used

def save_raw_from_url(cache_directory, target_directory, new_target_directory, anon_prefix, url, filename, category, directory, id, entry_id, rating, label, title, description, city, name, rawchecking, namedfiles):

    # if str(entry_id) not in try_raw_again:
    #     return




    ftp_folder = "/mnt/nlpa/raws"

    Path(target_directory).mkdir(parents=True, exist_ok=True)
    Path(new_target_directory).mkdir(parents=True, exist_ok=True)


    ftp_filename = os.path.join(ftp_folder, filename)

    raw_name, raw_suffix = os.path.splitext(filename)

    raw_filename = ''.join((raw_name, '-RAW', raw_suffix))
    xmp_filename = ''.join((raw_name, '-RAW', '.xmp'))
    new_target_filename =  os.path.join(new_target_directory, '%s_%s'%(anon_prefix,raw_filename))
    new_xmp_filename = os.path.join(new_target_directory, '%s_%s'%(anon_prefix,xmp_filename))

    if namedfiles:
        namedfile_prefix = '%s__%s__%s' % (name, id, entry_id)

        new_target_filename =  os.path.join(new_target_directory, '%s_%s'%(namedfile_prefix,raw_filename))
        new_xmp_filename = os.path.join(new_target_directory, '%s_%s'%(namedfile_prefix,xmp_filename))
        if str(entry_id) in inbookids.keys():
            label = "Blue"
            city = inbookids[entry_id]
            title = inbookids[entry_id]
        else:
            label = ""
            city = ""
    else:
        label = rawshecking

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


    xmp_content = xmp.format(rating=rating, filename=raw_filename, label=label, title=title, description=description, city=city, flag=rawchecking)
    with open(new_xmp_filename, "w") as text_file:
        text_file.write(xmp_content)



    if raw_suffix == 'jpg':
        data = {
            'Rating': rating,
            'Label': label,
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

def clear_metadata(metadata):
    for k in list(metadata.xmp_keys):
        del metadata[k]
    for k in list(metadata.iptc_keys):
        del metadata[k]
    for k in list(metadata.exif_keys):
        del metadata[k]



# Write XMP code
def write_xmp(path, data):
    if not MAKE_ANONYMOUS:
        try:
            metadata = pyexiv2.ImageMetadata(path)
            metadata.read()
            clear_metadata(metadata)
            metadata['Xmp.xmp.Label'] = str(data.get('Label',''))
            metadata['Xmp.xmp.Rating'] = int(data.get('Rating',0))
            metadata['Xmp.dc.title'] = data.get('Title','')
            metadata['Xmp.dc.description'] = data.get('Description','')
            metadata['Xmp.dc.creator'] = [data.get('Creator','')]
            metadata['Xmp.dc.rights'] = data.get('Creator','')
            metadata['Exif.Image.DateTime'] = datetime.datetime(2025, 6, 21, 0, 0, 0) - datetime.timedelta(0,round((data.get('State',2.4)-2.4)*2.083,3)*1000)
            metadata['Iptc.Application2.City'] = [str(data.get('City',0))]
            metadata['Iptc.Application2.City'] = [str(data.get('City',0))]
            metadata['Xmp.photoshop.City'] = [str(data.get('City',0))]
            metadata['Iptc.Application2.ProvinceState'] = [str(data.get('State',0))]
            metadata['Iptc.Application2.CountryName'] = [str(data.get('Country',0))]
            metadata['Iptc.Application2.SubLocation'] = [str(data.get('Sublocation',0))]
            metadata.write()
        except RuntimeError:
            print(f'xmp runtime error {path}')

    else:
        try:
            metadata = pyexiv2.ImageMetadata(path)
            metadata.read()
            clear_metadata(metadata)
            if GET_TOP_SCORES and data.get('State',2.4) >= 4:
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
            metadata['Xmp.photoshop.City'] = [str(data.get('City',0))]
            metadata['Iptc.Application2.ProvinceState'] = [str(data.get('State',0))]
            metadata['Iptc.Application2.CountryName'] = [str(data.get('Country',0))]
            metadata['Iptc.Application2.SubLocation'] = [str(data.get('Sublocation',0))]

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
            namedfiles,
            entrant,
            winner,
            quality,
            maxdim,
            skipjpgs,
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

    if namedfiles:
        namedfile = '%s__%s__%s.jpg' % (name, id, entry_id)
        target_filename = os.path.join(target_directory, namedfile)
        new_target_filename = os.path.join(new_target_directory, namedfile)

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
            d += '\ncountry={}\n\n'.format(country)
        else:
            title = 's{:.0f} m{:0>1.2f} r{:0>1.2f} v{:0>1.2f} vo{:0>1.2f}'.format(score, mean, raw_score, variance, variance_org)
            d += "R{R:.0f}.L{L:.0f}.M{M:.0f}.P{P:.0f}.H{H:.0f} ".format(**judge_entry_scores)
            d += "N{N:.0f}.Y{Y:.0f}.T{T:.0f}.A{M:.0f}.J{R:.0f}".format(**organiser_scores)
            d += '\ncountry={}\n\n'.format(country)


    if namedfiles:

        prize = ''

        prize_label = 'Green'
        if 'Award' in entrant:
            d += f"Award: {entrant.get('Award')}\n"
            d += f"Title: {entrant.get('Title')}\n"
            d += f"Caption\n{entrant.get('Caption')}\n\n"
        elif 'prize' in winner:
            prize = replace_from_position(winner['prize'].strip())
            category = replace_from_specials(winner['category'])
            award = f"{category}, {prize}"
            d+= f"Award: {award}\n"
        else:
            prize_label = ''

        if 'commended' in d.lower():
            prize_label = "Blue"

        if 'grand' in d.lower() or 'intimate' in d.lower() or 'abstract' in d.lower():
            if 'commended' in d.lower():
                prize_label = "Blue"
        else:
            prize_label = 'Yellow'
            if 'commended' in d.lower():
                prize_label = "Red"

        if ONLANDSCAPE:
            if country == 'nan':
                namecountry = f"{name}"
            else:
                namecountry = f"{name}, {country}"


            if 'Award' not in entrant:
                d = f"<strong style=\"font-style:normal\">{category}, {prize}</strong>\n<strong><em>{namecountry}</em></strong>\n<div style=\"text-align: left\"><strong>{entrant.get('Title', '')}\</strong>\n{entrant.get('Caption', '')}</div>"
            else:
                d = f"<strong style=\"font-style:normal\">{entrant.get('Award','')}</strong>\n<strong><em>{namecountry}</em></strong>\n<div style=\"text-align: left\"><strong>{entrant.get('Title','')}\</strong>\n{entrant.get('Caption','')}</div>"
            title = ''


    description = d


    if for_judge:

        # This is the label colour score
        label = ''
        rating = judge_entry_scores[for_judge]
        city = round(raw_score, 2)
        state = round(org_scores['mean'], 2)
        country = str(score) + '_' + str(round(mean, 2))
    else:
        if namedfiles:
            label = prize_label
        else:
            label = rawchecking
        rating = int(score)
        city = round(raw_score, 2)
        state = round(org_scores['mean'], 2)
        country = str(score) + '_' + str(round(mean, 2))
        sublocation = ','.join(row['entry_special_award'])

    if len(inbookids) != 0:
        if str(entry_id) in inbookids.keys():
            label = "Blue"
            city = inbookids[entry_id]
            title = inbookids[entry_id]
        else:
            label = ""
            city = ""
            title = ""



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
            save_raw_from_url(cache_directory, target_directory, new_target_directory, anon_prefix, 'https://submit.naturallandscapeawards.com%s'%f, f.split('/')[-1], category, directory, id, entry_id, rating, label, title, description, city, name, rawchecking, namedfiles)



    # Check to see if we've already processed this image
    if not dryrun and in_second_round:
        if not os.path.isfile(target_filename):


            if namedfiles:
                if not skipjpgs:
                    shutil.copy2(original_filename, target_filename)
            else:
                image = Image.open(original_filename)
                # **** RESIZE THIS IMAGE
                image.thumbnail((maxdim,maxdim))
                #image.thumbnail((1024,768))

                # Convert to sRGB (possible errors making things green in places in some images?)
                try:
                    image_conv = convert_to_srgb(image)
                except:
                    image_conv = image
                # ***** SAVE THE IMAGE AND SET COMPRESSION
                if not dryrun:
                    image_conv.save(target_filename, quality=quality, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))

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
                    'Sublocation': sublocation,

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
                    'Sublocation': sublocation,

                }
            if not dryrun and not skipjpgs:
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
                    'Sublocation': sublocation,
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
                    'Sublocation': sublocation,
                    'Creator': '',
                }

        if not skipjpgs:
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
            pdescription = row['project_description_one']
        else:
            title = row['project_title_two']
            pdescription = row['project_description_two']

        if not isinstance(title,str) and math.isnan(title):
            title = ''
        if not isinstance(description,str) and math.isnan(pdescription):
            pdescription = ''

        # whatever image it is in the project, make sure
        desc_target_filename =  os.path.join(target_directory, '00_project_description.jpg')
        new_desc_target_filename =  os.path.join(new_target_directory, '00_project_description.jpg')

        # if we're not on a dry run the create the project description if it doesn't already exist and also write the metadata to the project description
        if not dryrun and in_second_round:
            if not os.path.isfile(new_desc_target_filename):
                project_text(title, pdescription, new_desc_target_filename)
                if not anon:
                    data = {
                      'Rating': rating,
                      'Label': label,
                      'Title': title,
                      'Description': pdescription,
                      'Rights': country,
                      'Creator': name,
                        'City': raw_score,
                    'Sublocation': sublocation,

                    }
                else:
                    data = {
                    'Label': label,
                      'Rating': rating,
                    }
                if not skipjpgs:
                    write_xmp(new_desc_target_filename, data)
            else:
                if not os.path.isfile(desc_target_filename):
                    project_text(title, description, desc_target_filename)
                if not anon:
                    data = {
                      'Rating': rating,
                      'Label': label,
                      'Title': title,
                      'Description': pdescription,
                      'Rights': country,
                      'Creator': name,
                        'City': raw_score,
                    'Sublocation': sublocation,

                    }
                else:
                    data = {
                    'Label': label,
                      'Rating': rating,
                    }
                if not skipjpgs:
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

        if int(id) in port_id_list and int(entry_id) in port_scores_by_entry_id.keys() and (int(id) in skip_project or port_data[int(id)] >= portfolio_min_score):

            port_score = port_data[int(id)]

            # copy target_filename to
            port_target_directory = os.path.join(new_target, 'portfolio', '{:0>4.1f}-{}'.format(port_score,id))
            Path(port_target_directory).mkdir(parents=True, exist_ok=True)

            port_target_filename =  os.path.join(port_target_directory, anon_filename)

            if get_raws and in_second_round:
                for f in efiles:
                    save_raw_from_url(cache_directory, target_directory, port_target_directory, anon_prefix, 'https://submit.naturallandscapeawards.com%s'%f, f.split('/')[-1], category, directory, id, entry_id, rating, label, title, description, city, name, rawchecking, namedfiles)

            if not dryrun and ( not os.path.isfile(port_target_filename) or os.path.getsize(port_target_filename) < 100):
                image = Image.open(original_filename)
                # **************************************************************************************************************************
                image.thumbnail((maxdim, maxdim))
                #image.thumbnail((1024,768))
                try:
                    image_conv = convert_to_srgb(image)
                except:
                    image_conv = image
                # **************************************************************************************************************************
                if not skipjpgs:
                    image_conv.save(port_target_filename, quality=quality, format="JPEG",icc_profile = image_conv.info.get('icc_profile',''))
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
                if not dryrun and not skipjpgs:
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
                if not dryrun and not skipjpgs:
                    write_xmp(port_target_filename, data)

        return org_scores, judge_scores

#################################################################


if __name__ == "__main__":


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
    parser.add_argument("--quality", help="jpg quality", type=int, default=77)
    parser.add_argument("--maxdim", help="max image size", type=int, default=2048)
    parser.add_argument("--namedfiles", help="output named files", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--skipjpgs", help="no jpg out", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--target_base", help="base target directory name")
    # parser.add_argument("--filter_projects", help="list of project category names", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--portfolio_module", help="filename for portfolio module", default=None)
    parser.add_argument("--portfolio_top", help="amount of portfolios to portfolio_out", default=None)
    parser.add_argument("--config", help="yaml config file", default="config.yaml")



    args = parser.parse_args()
    directory = args.directory


    dryrun = args.dryrun
    get_raws = args.raws
    rawcsv = args.rawcheckcsv
    anon = args.anon
    minscore = args.minscore
    for_judge = args.judge
    comparison = args.comparison
    skipjpgs = args.skipjpgs

    maxdim = args.maxdim
    quality = args.quality

    namedfiles = args.namedfiles

    portfolio_module = args.portfolio_module
    portfolio_top = args.portfolio_top
    config = args.config





    with open(config) as f:
         yaml_data = yaml.safe_load(f)

    yaml_args = yaml_data['args']

    judges_data = yaml_data['judges']

    if not args.target_base:
        target_base = yaml_args.get('target_base')
    else:
        target_base = args.target_base
    source = yaml_args.get('originals', args.originals)
    full_csv = yaml_args.get('fullcsv', args.full_csv)

    judge_names = {}
    for k,v in judges_data.items():
        judge_names[v] = k


    portfolio_module = yaml_args.get('portfolio_module')
    entries_from_server = yaml_args.get('fullcsv', args.full_csv)
    print('entries_from_server=',entries_from_server)

    portfolio_out = yaml_args.get('portfolio_module', portfolio_module)




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
    'AD': '3 - Abstract and Details',
    'P1': '4 - Project',
    'P2': '4 - Project',
    }
    primary = "Primary (grade all)"
    secondary = "Secondary (optional extras)"

    # primary = "Results"
    # secondary = "Results-secondary"

    # label lookup for categories if we're in the portfolio SECTION
    category_label_lookup = {
    'GS': 'Blue',
    'IL': 'Green',
    'AD': 'Red',
    }

    # printing lowercase
    letters = string.ascii_lowercase


    # START OF ACTUAL PROCESSING

    dfentries = pd.read_csv(entries_from_server)

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

                if (str(user_id), str(entry_id)) in entry_rawchecking_lookup:
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

    winner_by_entry_id = {}
    entrant_by_entry_id = {}
    row_by_entry_id = {}
    if namedfiles:



        df = pd.read_csv(full_csv)
        l = len(df)

        for i in range(l):
            r = df.loc[i]
            if math.isnan(r['id']):
                continue

            entry_id = str(int(r['entry_id']))
            row_by_entry_id[entry_id] = r.to_dict()


        df = pd.read_csv('press_pack/winners.csv')
        l = len(df)

        winners_fields = "category,id,entry_id,filename,url,prize,name,email,country,facebook,instagram,website,bio".split(',')

        for i in range(l):
            winner = df.loc[i]
            entry_id = str(int(winner['entry_id']))
            winner_by_entry_id[entry_id] = winner.to_dict()



        output = []
        df = pd.read_csv('press_pack/entrants.csv')
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

            r = row_by_entry_id[entrant_id]

            name = entrant['Your Name (e.g. John Henry-Smythe, Arya Kumar, Zhang Chen)']


            if entrant_id in winner_by_entry_id:
                winner = winner_by_entry_id[entrant_id]

                id =str(winner['id'])
                entry_id = entrant_id
                fileid = f"{id[::-1]}_{entrant_id}_{id}"


                if winner['category'] == 'Projects':
                    prize = replace_from_position(winner['prize'].strip())
                    filename = f"PROJECTS/{prize} - {winner['name']}/{replace_from_position(winner['prize'])}-{winner['name']}-{fileid}.jpg"
                elif len(winner['category']) <= 2:
                    filename = f"SPECIALS/{replace_from_specials(winner['category'])}/{replace_from_position(winner['prize'])}-{winner['name']}-{fileid}.jpg"
                elif 'Year' in winner['prize']:
                    filename = f"00 Photograph of the Year, Winner - Margrit Schwarz - 23656__3690__65632.jpg"
                elif 'Photographer of the Year' in winner['category']:
                    prize = replace_from_position(winner['prize'].strip())
                    filename = f"PHOTOGRAPHER OF THE YEAR/{prize} - {winner['name']}/{replace_from_position(winner['prize']).strip().split(' ')[0]}-{winner['name']}-{fileid}.jpg"
                else:
                    filename = f"MAIN CATEGORIES/{replace_from_category(winner['category'])}/{replace_from_position(winner['prize'])}-{winner['name']}-{fileid}.jpg"

                award = f"{replace_from_specials(winner['category'])}, {winner['prize']}"
                category = winner['category']

            else:
                r = row_by_entry_id[entrant_id]
                id =str(r['id'])
                name = (r['name'])
                entry_id = entrant_id
                fileid = f"{id[::-1]}_{entrant_id}_{id}"
                category = replace_from_category(r['entry_category'])
                filename = f"EXTRAS/{name}--{category}--{fileid}.jpg"
                award = ''

            output_item = {
                'Filename': filename,
                'Name': name,
                'Award': award,
                'Photo ID': entrant_id,
                'Nationality': entrant['Where you live'],
                'Bio': entrant['Press Info'],
                'Profile Link Type': entrant['Type of Profile Link'],
                'Profile Link':  entrant['Profile Link'],
                'Title': entrant['Photograph Title'],
                'Caption': entrant['Press Info'],
                }

            entrant_by_entry_id[ entry_id ] = output_item

    # test_id = '59594'
    #
    # print(entrant_by_entry_id[ test_id ])
    # print(winner_by_entry_id[ test_id ])
    #
    # print(entrant_by_entry_id[test_id]['Award'])
    #
    # sys.exit()

    organiser_variance_totals = {
                'N': 0,
                'Y': 0,
                'T': 0,
                'R': 0,
                'M': 0,
    }
    # MAIN LOOP  CHECK IN SECOND ROUND!!!
    for i in range(len(dfentries)):
        printProgressBar(i + 1, len(dfentries), prefix = 'Progress:', suffix = 'Complete', length = 80)
        row = dfentries.loc[i]




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


        entrant = entrant_by_entry_id.get(str(entry_id), {})
        winner = winner_by_entry_id.get(str(entry_id), {})




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
            continue



        # This code is to build the score set if applicable (for portfolios or filtering for score levels)
        # only include final round and extra here
        #if not math.isnan(size) and str(entry_id) in judged_entry_ids:
        if not math.isnan(size):

            try:
                org_scores, judge_scores = resize(
                    noclash_filename,
                    category,
                    name,
                    str(int(entry_id)),
                    str(int(id)),
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
                    namedfiles,
                    entrant,
                    winner,
                    quality,
                    maxdim,
                    skipjpgs,
                )

                # if entry_id in missing_ids:
                #     print('in score resize {}'.format(entry_id))


                if org_scores is not None:



                    mean_score = (judge_scores['mean_all']*5 + org_scores['mean']*4)/9



                    score_set.append(mean_score)




                    if category not in ["P1","P2"]:

                        if id not in user_scores:
                            user_scores[id] = {'jscores': {entry_id : judge_scores['mean_all']},
                                               'oscores': {entry_id : org_scores['mean']},
                                               'scores': {entry_id : mean_score},
                                               'scoreset': {entry_id: {'j': judge_scores, 'o': org_scores} },
                                               }
                        else:

                            user_scores[id]['jscores'][entry_id] = judge_scores['mean_all']
                            user_scores[id]['oscores'][entry_id] = org_scores['mean']
                            user_scores[id]['scores'][entry_id] = mean_score
                            user_scores[id]['scoreset'][entry_id] = {'j': judge_scores, 'o': org_scores}




            except OSError as e:
                #exc_type, exc_obj, exc_tb = sys.exc_info()
                #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                #print(exc_type, fname, exc_tb.tb_lineno)

                print(traceback.format_exc())
                print(e)
                print('%s ERROR WITH %s for %s in %s (%s,%s)'%(e,filename,category,name,id,entry_id))
        else:
            print('fuckup')

        if entry_id in missing_ids:

            if judge_scores['scores'] == [0,0,0,0,0]:
                print ('round 2 {}'.format(entry_id))
            else:
                print ('round 1 {}'.format(entry_id))



    # This code builds the list of all scores and then includes only the top 6 entered.
    # The final total should be their portfolio score
    for user_id, score_data in user_scores.items():
        # build a tuple of the scores in order to sort them
        total_scores = []
        for entry_id, score in score_data['scores'].items():
            total_scores.append((entry_id, score))
        total_scores.sort(key=lambda tup: tup[1], reverse=True)
        # Limit to the top 6  imags
        topsix = total_scores[:6]
        # build a lookup of user to score compilation data
        score_data['items'] = {}
        for t in topsix:
            score_data['items'][t[0]] = t[1]
        # Get the total score for the top six images
        total = 0
        for s in total_scores[:6]:
            total += s[1]
        score_data['total'] = total


    # Some code to sort the scores.
    sorted_scores = []
    for user_id, score_data in user_scores.items():
        sorted_scores.append( (user_id, score_data['total']) )
        sorted_scores.sort(key=lambda tup: tup[1], reverse=True)


    if portfolio_out:

        with open(portfolio_out, 'w') as f:
        # This prints out the "portfolio.py" contents
            f.write("port_ids = [\n")

            if portfolio_top:
                ss = sorted_scores[:portfolio_top]
            else:
                ss = sorted_scores
            for t in ss:
                f.write("({0:}, {1:.2f}),\n".format(*t))
            f.write("]\n")

            f.write("scores_dict = ")
            f.write(json.dumps(user_scores))

            from collections import Counter
            f.write('#%s\n'%Counter(score_set))
