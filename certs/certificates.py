from PIL import Image, ImageFont, ImageDraw, ImageFilter
import re
import random


def can_render(text, font):
    """Return True if font has glyphs for all characters in text."""
    for char in text:
        if not font.getmask(char).getbbox() and ord(char) != 32:
            print(f'char={char}, {ord(char)}')
            return False
    return True


def crop_project(filepath: str) -> str:
    # Split directory and file
    directory, filename = os.path.split(filepath)

    # Extract the "project-[number]" part
    match = re.match(r"(project-\d+)", filename)
    if not match:
        raise ValueError(f"Filename '{filename}' does not match expected pattern")

    base = match.group(1)
    new_name = f"{base}-crop.jpg"

    # Rejoin with original directory
    return os.path.join(directory, new_name)



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

specials = {
    'M,': 'Mountains,',
    'WL,': 'Woodland,',
    'TL,': 'Tropical Landscapes,',
    'S,': 'Seascapes,',
    'RG,': 'Rocks and Geology,',
    'IB,': 'In Your Backyard,',
    'FW,': 'Frozen Worlds,',
    'DL,': 'Desert Landscapes,',
    'Scenic': 'Landscape',
    'and Details': 'Landscape',
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

    for key, value in specials.items():
        text = text.replace(key,str(value))
    return text

import sys, os



def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height

stage_intro_text = "Stage reached:"

star_stage = 1

background =  'assets/award-background-final-nosigsq.jpg'

stage_text_spacing = 48

photo_bounds_wide = [(200,370), (1160,860)] # 960, 460
photo_bounds_tall = [(160,400), (640,1230)] # 480, 830

score_font = ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 50)
header_font = ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 42)
stage_font = ImageFont.truetype('assets/GrotaSansAltRd-Medium.otf', 32)
stage_bold_font = ImageFont.truetype('assets/GrotaSansAltRd-Bold.otf', 32)
intro_stage_font = ImageFont.truetype('assets/GrotaSansAltRd-Medium.otf', 27)
category_font = ImageFont.truetype('assets/GrotaSansAltRd-Medium.otf', 32)
judge_font = ImageFont.truetype('assets/GrotaSansAltRd-Medium.otf', 28)

header_font_j = ImageFont.truetype('assets/NotoSansTC-VariableFont_wght.ttf', 42)


def dropShadow( image, offset=(6,6), background=0xffffff, shadow=0xBBBBBB,
                border=8, iterations=3):
  """
  Add a gaussian blur drop shadow to an image.

  image       - The image to overlay on top of the shadow.
  offset      - Offset of the shadow from the image as an (x,y) tuple.  Can be
                positive or negative.
  background  - Background colour behind the image.
  shadow      - Shadow colour (darkness).
  border      - Width of the border around the image.  This must be wide
                enough to account for the blurring of the shadow.
  iterations  - Number of times to apply the filter.  More iterations
                produce a more blurred shadow, but increase processing time.
  """

  # Create the backdrop image -- a box in the background colour with a
  # shadow on it.
  totalWidth = image.size[0] + abs(offset[0]) + 2*border
  totalHeight = image.size[1] + abs(offset[1]) + 2*border
  back = Image.new(image.mode, (totalWidth, totalHeight), background)

  # Place the shadow, taking into account the offset from the image
  shadowLeft = border + max(offset[0], 0)
  shadowTop = border + max(offset[1], 0)
  back.paste(shadow, [shadowLeft, shadowTop, shadowLeft + image.size[0],
    shadowTop + image.size[1]] )

  # Apply the filter to blur the edges of the shadow.  Since a small kernel
  # is used, the filter must be applied repeatedly to get a decent blur.
  n = 0
  while n < iterations:
    back = back.filter(ImageFilter.BLUR)
    n += 1

  # Paste the input image onto the shadow backdrop
  imageLeft = border - min(offset[0], 0)
  imageTop = border - min(offset[1], 0)
  back.paste(image, (imageLeft, imageTop))

  return back


def build_cert(target_filename, images, scores, name, subheader, stage, is_portfolio, prize, year, dryrun, cachedir):



    if name[0].isupper() and name[1].isupper() and name != "DCraig Young":
        # print(name)
        name = name.title()
        # print(name)

    if name[0].islower() and name[1].islower():
        # print(name)
        name = name.title()
        # print(name)




    orders = {}
    orders[12] = [0,2,4,3,1,5,7,9,8,6]
    orders[11] = [0,2,4,3,1,5,7,9,8,6]
    orders[10] = [0,2,4,3,1,5,7,9,8,6]
    orders[9] =  [0,2,4,3,1,5,7,8,6]
    orders[8] =  [0,2,3,1,4,6,7,5]
    orders[7] =  [0,2,3,1,4,6,5]
    orders[6] =  [0,2,1,3,5,4]
    orders[5] =  [0,2,1,3,4]

    num_projects = len(images)

    if num_projects >4:
        temp_images = []
        for i in images:
            example_image = Image.open(i)
            t_w, t_h = example_image.size
            aspect_ratio = t_w/t_h
            temp_images.append( ( os.path.join(i), aspect_ratio ) )

        temp_images.sort(key=lambda tup: tup[1], reverse=True)

        images = []
        for i in range(num_projects):
            images.append(temp_images[ orders[num_projects][i] ][0])




    subheader = subheader[:90]


    if len(images) >1 and not is_portfolio:
        is_project = True
    else:
        is_project = False


    example_image = Image.open(images[0])
    w, h = example_image.size


    if w/h >= 1 or is_project or is_portfolio:

        format = 'wide'
        photo_bounds = photo_bounds_wide
        star_x_column = 773
        star_y_row_1 = 881
        stage_x, stage_y = (205, 881)
    else:
        format = 'tall'
        photo_bounds = photo_bounds_tall
        star_x_column = 754
        star_y_row_1 = 767
        stage_x, stage_y = (754, 400)

    b_w = photo_bounds[1][0] - photo_bounds[0][0]
    b_h = photo_bounds[1][1] - photo_bounds[0][1]


    name_x, name_y = (696, 280)
    category_x, category_y = (696, 330)




    if is_project or is_portfolio:
        w = b_w
        h = b_h
    else:

        example_image = Image.open(images[0])
        example_image.thumbnail((b_w, b_h), Image.LANCZOS)


        w, h = example_image.size


    x_spacing = 25
    y_spacing = 45

    e_x, e_y = (photo_bounds[0][0], photo_bounds[0][1])


    if format == 'wide' or is_project or is_portfolio:
        e_x = e_x + int( (b_w-w)/2 )
        stage_y = stage_y - int(b_h-h)
        star_y_row_1 = star_y_row_1 - int(b_h-h)
        if ((is_project or is_portfolio) and stage >= star_stage) or (not is_project and not is_portfolio and stage >= star_stage):
            stage_x = stage_x
        else:
            stage_x = 444
    else:
        e_x = e_x + int( (b_w-w)/2 )
        star_x_column = star_x_column - int( (b_w-w)/2 )
        stage_x = stage_x - int( (b_w-w)/2 )
        if stage < 4:
            stage_y = stage_y+30




    star_position = {}

    for judge in range(8):
        for star in range(10):
            x = star_x_column + star*x_spacing
            y = star_y_row_1+judge*y_spacing
            star_position[(judge+1,star+1)] = (x,y)

    bckgnd = Image.open(background).convert('RGBA')  # Convert to mode supporting alpha




    star_colour = Image.open('assets/star-evensmaller.jpg')
    star_grey = Image.open('assets/star-evensmaller-grey.jpg')




    if is_project or is_portfolio:

        margin_x = 20
        margin_y = 0
        y_offset = b_h//2
        yy_offset = b_h//2

        x_offset = 0
        num_row = 5
        if num_projects <9:
            num_row = 4
            x_offset = 0
        if num_projects <7:
            num_row = 3
            x_offset = 0


        for n,p in enumerate(images):

            if not os.path.isfile(p):
                continue

            i_w = b_w//num_row
            i_h = b_h//2
            i_x = (b_w//num_row)*(n%num_row)
            i_y = (b_h//2)*(n//num_row)


            example_image = Image.open(p)
            example_image.thumbnail((i_w-margin_x,i_h-margin_y),Image.LANCZOS)
            t_w, t_h = example_image.size

            if n//num_row == 0:
                if (i_h-t_h) < y_offset:
                    y_offset = (i_h-t_h)

            else:
                i_x = i_x + (num_projects%2)*i_w//2
                i_y += -y_offset+40
                if (i_h-t_h) < yy_offset:
                    yy_offset = (i_h-t_h)



            i_x += (i_w - t_w)//2
            #i_y += (i_h - t_h)//2
            example_image = dropShadow(example_image)

            tmp_img = Image.new('RGBA', bckgnd.size, color=(0,0,0,0))
            tmp_img.paste(example_image, (e_x+i_x+ + (x_offset*i_h)//2, e_y+i_y))



            bckgnd.alpha_composite(tmp_img)


    else:
        example_image = Image.open(images[0])

        example_image.thumbnail((w,h),Image.LANCZOS)

        example_image = dropShadow(example_image)

        tmp_img = Image.new('RGBA', bckgnd.size, color=(0,0,0,0))
        tmp_img.paste(example_image, (e_x, e_y))
        bckgnd.alpha_composite(tmp_img)


    writing = ImageDraw.Draw(bckgnd)


    offset_y = 0
    if is_project or is_portfolio:
        offset_y = -(y_offset-40+yy_offset-40)
    else:
        offset_y = 30




    # coordinate to extract us offset_Y AND
    #     x_spacing = 25
    #     y_spacing = 45
    # x_width =

    if ((is_project or is_portfolio) and stage >= star_stage) or (not is_project and not is_portfolio and stage >= star_stage):



        for judge, score in enumerate(scores):



            if is_portfolio:
                if len(scores) == 5:
                    judge_label = 'Judge'
                    judge_offset_x = 0

                    adjusted_score = int(float(score) / 5 * 7 + 2)
                else:
                    judge_label = 'Pre-Judge'
                    judge_offset_x = 15

                    adjusted_score = int(float(score) / 4 * 7 + 1)
            else:
                if stage >= 3:
                    judge_label = 'Judge'
                    judge_offset_x = 0

                    adjusted_score = int(float(score) / 5 * 7 + 2)
                else:
                    judge_label = 'Pre-Judge'
                    judge_offset_x = 15

                    adjusted_score = int(float(score) / 4 * 7 + 1)

            for s in range(10):
                if s>adjusted_score:
                    star = star_grey
                else:
                    star = star_colour
                star_x, star_y = star_position[ (judge+1,s+1) ]
                tmp_img = Image.new('RGBA', bckgnd.size, color=(0,0,0,0))
                tmp_img.paste(star, (star_x+140+judge_offset_x, star_y+offset_y))
                bckgnd.alpha_composite(tmp_img)
        for judge, score in enumerate(scores):
            adjusted_score = int(float(score)/5*7+3)
            star_x, star_y = star_position[ (judge+1,1) ]
            writing.text((star_x,star_y+2+offset_y),"{} {}".format(judge_label,judge+1),(150,150,150),font=judge_font)

    print(name)
    if can_render(name, header_font):
        hf = header_font
    else:
        print('selecting fallback font')
        hf = header_font_j

    tw, th = textsize(name, font=hf)
    # if prize:
    #     tmp_img = Image.new('RGBA', bckgnd.size, color=(0,0,0,0))
    #     prize_icon = Image.open('prize-icon-{}.jpg'.format(4-prize))
    #     prize_thumbnail = prize_icon.thumbnail((40,40),Image.LANCZOS)
    #     tmp_img.paste(prize_icon, ((name_x+int(tw/2)+40,name_y-int(th/2))))
    #     bckgnd.alpha_composite(tmp_img)
    if prize == "Photograph of the Year, Winner" or (prize is not None and prize.startswith("Photographer of the Year")):
        subheader = prize
    elif prize is not None and prize.startswith("Project of the Year"):
        subheader = prize
    elif prize is not None:
        subheader = '{}, {}'.format(subheader, prize)

    subheader = replace_from_specials(subheader)


    writing.text((name_x-int(tw/2),name_y-int(th/2)),"{}".format(name),(0,0,0),font=hf)

    tw, th = textsize("{}".format(subheader), font=category_font)
    writing.text((category_x-int(tw/2),category_y-int(th/2)),"{}".format(subheader),(80,80,80),font=category_font)









    if is_project:
        stage_text = {}
        stage_text[1] = "1. Pre-Judging (235 - 100%)"
        stage_text[2] = "2. Main Judging  (159 - 68%)"
        stage_text[3] = "3. Second Round  (97 - 41%)"
        stage_text[4] = "4. Pre-Finals (66 - 28%)"
        stage_text[5] = "5. Final Live Judging (39 - 16.6%)"
        stage_text[6] = "6. Final Voting (9 - 3.8%)"


    elif is_portfolio:
        stage_text = {}
        stage_text[1] = "1. First Pre-Judging  (811 - 100%)"
        stage_text[2] = "2. Second Pre-Judging (589 - 73%)"
        stage_text[3] = "3. Main Judging (310 - 38%)"
        stage_text[4] = "4. Pre-Finals (146 - 18%)"
        stage_text[5] = "5. Final Live Judging (10 - 1.2%)"
        stage_text[6] = "6. Final Voting (6 - 0.7%)"

    else:

        stage_text = {}
        stage_text[1] = "1. First Pre-Judging (8753 - 100%)"
        stage_text[2] = "2. Second Pre-Judging (5722 - 65%)"
        stage_text[3] = "3. Main Judging (2684 - 31%)"
        stage_text[4] = "4. Pre-Finals (609 - 7%)"
        stage_text[5] = "5. Final Live Judging (202 - 2.3%)"
        stage_text[6] = "6. Final Voting (60 - 0.7%)"



    writing.text((stage_x,stage_y+offset_y),stage_intro_text,(0,0,0),font=intro_stage_font)

    # Only show the last stages if they're in the last stages
    if not is_project and not is_portfolio and stage <4:
        stage_text.pop(6)
        stage_text.pop(5)

    for stage_row in range(len(stage_text.keys())):
        if stage > stage_row+1:
            stage_row_font = stage_font
            stage_row_colour = (0,0,0)
        elif stage == stage_row+1:
            stage_row_font = stage_bold_font
            stage_row_colour = (0,0,0)
        else:
            stage_row_font = stage_font
            stage_row_colour = (200,200,200)



        writing.text((stage_x,stage_y+offset_y+stage_text_spacing*(stage_row+1)),stage_text[stage_row+1],stage_row_colour,font=stage_row_font)


    try:
        image_conv = convert_to_srgb(bckgnd)
    except:
        image_conv = bckgnd
    out = image_conv.convert('RGB')

    if not dryrun:
        out.save(target_filename, quality=92, format="JPEG",icc_profile = out.info.get('icc_profile',''))

    if is_project or is_portfolio:
        if is_project:
            output_path = crop_project(target_filename)
        else:
            output_path = os.path.join(os.path.dirname(target_filename), 'combined-portfolio-crop.jpg')

        crop_box = (220, 380, 1180, 860+offset_y+20)
        cropped_img = out.crop(crop_box)
        cropped_img.save(output_path)


    if is_portfolio:
        type = 'portfolio'
    elif is_project:
        type = 'project'
    else:
        type = 'entry'

    data = {
        'target_filename': target_filename,
        'name': name,
        'subheader': subheader,
        'stage_text': stage_text[stage],
        'prize': prize,
        'type': type,
    }
    return data


if __name__ == "__main__":

    is_project = False

    if is_project:

        temp_images = {}
        for p in range(10):
            temp_images[p] = 'sample_projects_2/p-{}.jpg'.format(p+1)

        images = []

        for n, p in temp_images.items():
            if os.path.isfile(p):
                images.append(p)

    else:
        images = ['example-tall.jpg']



    scores = [0,1,4,5,1,4,0,3]

    target_filename = "test.png"
    name = "Theo Bosboom"
    subheader = "European Canyons"
    stage = 4

    is_portfolio = False

    build_cert(target_filename, images, scores, name, subheader, stage, is_portfolio)
