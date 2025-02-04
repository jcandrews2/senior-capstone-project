import argparse
import json
import cv2
from pytesseract import pytesseract, Output
# from funcs import *
import os
import glob
import numpy as np
from difflib import SequenceMatcher

def apex_OCR(img_file):
    # damage dealt
    DDs = []
    get_DD_crops(img_file)
    for i in range(3):
        txt = read_DD_crops(f'DD_crops_temp/crop{i}.jpg')[:-1]
        DDs.append(txt.replace(',', ''))

    # KAK
    KAKs = []
    get_KAK_crops(img_file)
    for i in range(3):
        KAKs.append(read_KAK_crops(f'KAK_crops_temp/crop{i}.jpg'))

    out = {"game_id" : '_',
           "school" : "_",
           "players" : []
           }

    log = [['.', '.' ,'.'], ['.' ,'.','.'], ['.', '.' ,'.']]


    for index, val in enumerate(KAKs):
        val = val.replace('_', '/')
        parts = val.split('/')
        # print(val, '>',parts, '>', len(parts))

        for idx, p in enumerate(parts):
            print(p)
            log[index][idx] = p
        

    # print(log)



    for i in range(3):
        # out["players"].append({"kak" : KAKs[i], "damage": DDs[i]})
        out['players'].append({'palyer_name':'_',
                                'kills':log[i][0],
                                'assists':log[i][1],
                                'knocks':log[i][2],
                                'damage':DDs[i],
                                'score':'_',
                                'placement':'_',
                                'game_number':'_',
                                'week_number':'_'})
    
    return out





# get kills/assists/knocks
def get_KAK_simple(img_file):
    img = cv2.imread(img_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    cv2.imwrite('init_image.jpg', bin)

    d = pytesseract.image_to_data(gray, output_type=Output.DICT, lang='eng', config='--psm 6 -c tessedit_char_whitelist="0123456789/"') #abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ



    box_img = img.copy()

    # detected boxes
    n_boxes = len(d['text'])

    all_text = []
    for i in range(n_boxes):
        if int(d['conf'][i]) > 10:  # Adjust confidence threshold
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            # expand
            x = max(x - 5 - 5, 0)
            y = max(y - 5 - 5, 0)
            w = w + 10 + 10
            h = h + 10 + 10

            # rectangle
            box_img = cv2.rectangle(box_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # crop
            crop = img[y:y + h, x:x + w]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
            _, crop = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
            crop = scale_img(crop, 150)

            text = pytesseract.image_to_string(crop, config='--psm 6 -c tessedit_char_whitelist="0123456789/"')
            print(f"Detected text in box {i}: {text.strip()}")
            if i == 17 or i == 18 or i == 19:
                cv2.imwrite(f'KAK_crops_simple/crop_sample{i}.png', crop)
            
            all_text.append(text[:-1])

    cv2.imwrite('processed_boxed_image.jpg', box_img)
    return list(filter(None, all_text))

def get_KAK(img_file, pn):
    files = glob.glob('KAK_crops_temp/*')
    for f in files:
        os.remove(f)

    img = cv2.imread(img_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(gray , 127, 255, cv2.THRESH_BINARY)
    AT = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    cv2.imwrite('bin.jpg', bin)
    cv2.imwrite('gray.jpg', gray)
    cv2.imwrite('AT.jpg', AT)

    d = pytesseract.image_to_data(gray, output_type=Output.DICT, lang='eng', config='--psm 6 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"')#0123456789/

    box_img = img.copy()

    # detected boxes
    n_boxes = len(d['text'])

    # all_text = []
    text_dict = {}
    for i in range(n_boxes):
        if int(d['conf'][i]) > -1:  # Adjust confidence threshold
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            # expand
            x = max(x - 5 - 5, 0)
            y = max(y - 5 - 5, 0)
            w = w + 10 + 10
            h = h + 10 + 10

            # rectangle
            box_img = cv2.rectangle(box_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # crop
            crop = img[y:y + h, x:x + w]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
            _, crop = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
            crop = scale_img(crop, 150)

            text = pytesseract.image_to_string(crop, config='--psm 6')# -c tessedit_char_whitelist="0123456789/"')
            
            if (len(text) > 5):
                text_dict[i] = text[:-1]
            
            # print(f"Detected text in box {i}: {text.strip()}")
    

    target = "Kills / Assists / Knocks"
    similarities = [(key, val, str_similarity(val, target)) for key, val in text_dict.items()]
    top3_similarities = sorted(similarities, key=lambda x: x[2], reverse=True)[:3]
    top3_similarities = sorted(top3_similarities, key=lambda x:x[0], reverse=False)

    print(top3_similarities)

    cv2.imwrite('processed_boxed_image.jpg', box_img)

    kak_img = img.copy()
    all_h = []
    all_y = []
    all_w = []
    ## get the boxes on KAK from target boxes
    for item in top3_similarities:
        all_h.append(d['height'][item[0]])
        all_y.append(d['top'][item[0]])
        all_w.append(d['width'][item[0]])

    ideal_h = min(all_h)
    ideal_y = max(all_y)
    ideal_w = min(all_w)

    print('h: ', ideal_h)
    print('w: ', ideal_w)
    print('ratio: ', ideal_h/ideal_w)
    if ideal_h / ideal_w > .10:
        cut = int((ideal_h - (ideal_w * .10)) / 2)
        ideal_y += cut
        ideal_h -= cut

    for idx, item in enumerate(top3_similarities):
        # all_h.append(d['height'][item[0]])
        (x, y, w, h) = (d['left'][item[0]], d['top'][item[0]], d['width'][item[0]], d['height'][item[0]])

        all_h.append(h)
        x = x-10
        y = ideal_y+17
        w = ideal_w
        h = ideal_h + 20




        # rectangle
        kak_img = cv2.rectangle(kak_img, (x, y), (x + w, y + h), (0, 255, 0), 2) # G 
        kak_img = cv2.rectangle(kak_img, (x, ideal_y), (x + ideal_w, ideal_y + ideal_h), (255, 0, 0), 2) # B


        # crop
        crop = img[y:y + h, x:x + w]


        fname = f'KAK_crops_temp/crop{idx}.jpg'
        cv2.imwrite(fname, crop)

        # print(pytesseract.image_to_string(crop, config='--psm 8 -c tessedit_char_whitelist="0123456789/"'))
        

    fname=f'target_img/kak_img{pn}.jpg'
    cv2.imwrite(fname, kak_img)


    all_KAK = []
    dir = 'KAK_crops_temp'
    all_files = []
    for filename in os.listdir(dir):
        print(filename)
        f = os.path.join(dir, filename)
        all_files.append(f)
    all_files.sort()
    all_files = all_files[1:]
    

    print(len(all_files))
    for file in all_files:   
        box = cv2.imread(file)
        print(f'getting {file}')
        each_box = get_char_boxes(box)
        all_KAK.append(each_box)



    # return all_KAK
    return all_KAK




    files = glob.glob('KAK_crops_char/*')
    for f in files:
        os.remove(f)


    # dims
    # height, width = img.shape[:2]
    
    # # bounding boxes
    # d = pytesseract.image_to_boxes(img, output_type=Output.DICT, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')
    # n_boxes = len(d['char'])
    # print('num boxes: ', n_boxes)

    # whole_txt = ''
    # for i in range(n_boxes):
    #     char = d['char'][i]
    #     # print('default: ', char)

    #     x1, y2, x2, y1 = d['left'][i], d['top'][i], d['right'][i], d['bottom'][i]
        
    #     # adjust for OpenCV (it uses top-left origin)
    #     y1, y2 = height - y1, height - y2

    #     # padding
    #     padding = 10
    #     x1 = max(x1 - padding, 0)
    #     y1 = min(y1 + padding, height)
    #     x2 = min(x2 + padding, width)
    #     y2 = max(y2 - padding, 0)
        
    #     # crop
    #     # crop = img[y2:y1, x1:x2]
    #     crop = img[y2:y1, x1:x2]

    #     if (i == 0):
    #         crop = scale_img(crop,80)
        
    #     cv2.imwrite(f'KAK_crops_char/char{i}.png', crop)

    #     text = pytesseract.image_to_string(crop, config='--psm 6 -c tessedit_char_whitelist="0123456789/"')
    #     print(f'char{i}: ', text)
    #     whole_txt += text
    #     # print(text)
    

    
    # return whole_txt
        
    # height = img.shape[0]
    # width = img.shape[1]

    # d = pytesseract.image_to_boxes(img, output_type=Output.DICT, config='--psm 6')
    
    # n_boxes = len(d['char'])
    # print('num boxes: ', n_boxes)
    # for i in range(n_boxes):
    #     (text,x1,y2,x2,y1) = (d['char'][i],d['left'][i],d['top'][i],d['right'][i],d['bottom'][i])
    #     cv2.rectangle(img, (x1,height-y1), (x2,height-y2) , (0,255,0), 2)
    # cv2.imshow('img',img)
    # cv2.waitKey(0)

# game code
def get_game_code(img_file):
        # files = glob.glob('DD_crops_temp/*')
    # for f in files:
    #     os.remove(f)

    img = cv2.imread(img_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(gray , 127, 255, cv2.THRESH_BINARY)
    AT = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    cv2.imwrite('bin.jpg', bin)

    d = pytesseract.image_to_data(bin, output_type=Output.DICT, lang='eng', config='--psm 6 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"')#0123456789/

    box_img = img.copy()

    # detected boxes
    n_boxes = len(d['text'])

    # all_text = []
    text_dict = {}
    for i in range(n_boxes):
        if int(d['conf'][i]) > -1:  # Adjust confidence threshold
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            # expand
            x = max(x - 5 - 5, 0)
            y = max(y - 5 - 5, 0)
            w = w + 10 + 10
            h = h + 10 + 10

            # rectangle
            if i == 0:
                box_img = cv2.rectangle(box_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # crop
            crop = img[y:y + h, x:x + w]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
            _, crop = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
            crop = scale_img(crop, 150)

            text = pytesseract.image_to_string(crop, config='--psm 6')# -c tessedit_char_whitelist="0123456789/"')
            
            if (len(text) > 5):
                text_dict[i] = text[:-1]
    
    cv2.imwrite('box_im.jpg', box_img)

## Squad Placed
def get_squad_placed(img_file):
    # files = glob.glob('DD_crops_temp/*')
    # for f in files:
    #     os.remove(f)

    img = cv2.imread(img_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(gray , 127, 255, cv2.THRESH_BINARY)
    AT = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    d = pytesseract.image_to_data(gray, output_type=Output.DICT, lang='eng', config='--psm 6 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"')#0123456789/

    box_img = img.copy()

    # detected boxes
    n_boxes = len(d['text'])

    # all_text = []
    text_dict = {}
    for i in range(n_boxes):
        if int(d['conf'][i]) > -1:  # Adjust confidence threshold
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            # expand
            x = max(x - 5 - 5, 0)
            y = max(y - 5 - 5, 0)
            w = w + 10 + 10
            h = h + 10 + 10

            # rectangle
            box_img = cv2.rectangle(box_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # crop
            crop = img[y:y + h, x:x + w]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
            _, crop = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
            crop = scale_img(crop, 150)

            text = pytesseract.image_to_string(crop, config='--psm 6')# -c tessedit_char_whitelist="0123456789/"')
            
            if (len(text) > 5):
                text_dict[i] = text[:-1]
    
    cv2.imwrite('box_im.jpg', box_img)

    target = "SQUAD"
    similarities = [(key, val, str_similarity(val, target)) for key, val in text_dict.items()]
    top_sim = sorted(similarities, key=lambda x: x[2], reverse=True)[:1]
    top_sim = sorted(top_sim, key=lambda x:x[0], reverse=False)

    # dd_img = img.copy()
    # all_h = []
    # all_y = []
    # all_w = []
    ## get the boxes on dd from target boxes
    # for item in top_sim:
        # all_h.append(d['height'][item[0]])
        # all_y.append(d['top'][item[0]])
        # all_w.append(d['width'][item[0]])

    # ideal_h = min(all_h)
    # ideal_y = max(all_y)
    # ideal_w = min(all_w)

    # print('h: ', ideal_h)
    # print('w: ', ideal_w)
    # print('ratio: ', ideal_h/ideal_w)\\


    # if ideal_h / ideal_w > .10:
    #     cut = int((ideal_h - (ideal_w * .10)) / 2)
    #     ideal_y += cut
    #     ideal_h -= cut

    # for idx, item in enumerate(top_sim):
    #     # all_h.append(d['height'][item[0]])
    #     (x, y, w, h) = (d['left'][item[0]], d['top'][item[0]], d['width'][item[0]], d['height'][item[0]])

    #     # all_h.append(h)
    #     x = x-10
    #     y = y+15
    #     w = w
    #     h = h + 20

    #     # rectangle
    #     # dd_img = cv2.rectangle(dd_img, (x, y), (x + w, y + h), (0, 255, 0), 2) # G 
    #     # dd_img = cv2.rectangle(dd_img, (x, ideal_y), (x + ideal_w, ideal_y + ideal_h), (255, 0, 0), 2) # B

    #     # crop
    #     crop = img[y:y + h, x:x + w]
    #     txt = pytesseract.image_to_string(crop)

    #     # fname = f'DD_crops_temp/crop{idx}.jpg'
    #     # cv2.imwrite(fname, crop)
    #     \

    (x, y, w, h) = (d['left'][top_sim[0][0]], d['top'][top_sim[0][0]], d['width'][top_sim[0][0]], d['height'][top_sim[0][0]])

    # all_h.append(h)
    x = x + 80
    y = y - 15
    w = w + 10
    h = h + 45

    # rectangle
    # dd_img = cv2.rectangle(dd_img, (x, y), (x + w, y + h), (0, 255, 0), 2) # G 
    # dd_img = cv2.rectangle(dd_img, (x, ideal_y), (x + ideal_w, ideal_y + ideal_h), (255, 0, 0), 2) # B

    # crop
    crop = img[y:y + h, x:x + w]
    crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(crop , 127, 255, cv2.THRESH_BINARY)

    cv2.imwrite('sq_placed.jpg', bin)

    

    print('sq: ',pytesseract.image_to_string(bin))

    # return txt





### Finals ###
## DD
def get_DD_crops(img_file):

    files = glob.glob('DD_crops_temp/*')
    for f in files:
        os.remove(f)

    img = cv2.imread(img_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(gray , 127, 255, cv2.THRESH_BINARY)
    AT = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    d = pytesseract.image_to_data(gray, output_type=Output.DICT, lang='eng', config='--psm 6 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"')#0123456789/

    box_img = img.copy()

    # detected boxes
    n_boxes = len(d['text'])

    # all_text = []
    text_dict = {}
    for i in range(n_boxes):
        if int(d['conf'][i]) > -1:  # Adjust confidence threshold
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            # expand
            x = max(x - 5 - 5, 0)
            y = max(y - 5 - 5, 0)
            w = w + 10 + 10
            h = h + 10 + 10

            # rectangle
            box_img = cv2.rectangle(box_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # crop
            crop = img[y:y + h, x:x + w]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
            _, crop = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
            crop = scale_img(crop, 150)

            text = pytesseract.image_to_string(crop, config='--psm 6')# -c tessedit_char_whitelist="0123456789/"')
            
            if (len(text) > 5):
                text_dict[i] = text[:-1]
    

    target = "Damage Dealt"
    similarities = [(key, val, str_similarity(val, target)) for key, val in text_dict.items()]
    top3_similarities = sorted(similarities, key=lambda x: x[2], reverse=True)[:3]
    top3_similarities = sorted(top3_similarities, key=lambda x:x[0], reverse=False)

    dd_img = img.copy()
    all_h = []
    all_y = []
    all_w = []
    ## get the boxes on dd from target boxes
    for item in top3_similarities:
        all_h.append(d['height'][item[0]])
        all_y.append(d['top'][item[0]])
        all_w.append(d['width'][item[0]])

    ideal_h = min(all_h)
    ideal_y = max(all_y)
    ideal_w = min(all_w)

    # print('h: ', ideal_h)
    # print('w: ', ideal_w)
    # print('ratio: ', ideal_h/ideal_w)
    if ideal_h / ideal_w > .10:
        cut = int((ideal_h - (ideal_w * .10)) / 2)
        ideal_y += cut
        ideal_h -= cut

    for idx, item in enumerate(top3_similarities):
        # all_h.append(d['height'][item[0]])
        (x, y, w, h) = (d['left'][item[0]], d['top'][item[0]], d['width'][item[0]], d['height'][item[0]])

        all_h.append(h)
        x = x-10
        y = ideal_y+15
        w = ideal_w
        h = ideal_h + 20

        # rectangle
        dd_img = cv2.rectangle(dd_img, (x, y), (x + w, y + h), (0, 255, 0), 2) # G 
        dd_img = cv2.rectangle(dd_img, (x, ideal_y), (x + ideal_w, ideal_y + ideal_h), (255, 0, 0), 2) # B

        # crop
        crop = img[y:y + h, x:x + w]

        fname = f'DD_crops_temp/crop{idx}.jpg'
        cv2.imwrite(fname, crop)

def read_DD_crops(img_file):
    return pytesseract.image_to_string(img_file)


## KAK
def get_KAK_crops(img_file):
    files = glob.glob('KAK_crops_temp/*')
    for f in files:
        os.remove(f)

    img = cv2.imread(img_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, bin = cv2.threshold(gray , 127, 255, cv2.THRESH_BINARY)
    AT = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

    d = pytesseract.image_to_data(gray, output_type=Output.DICT, lang='eng', config='--psm 6 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"')#0123456789/

    box_img = img.copy()

    # detected boxes
    n_boxes = len(d['text'])

    # all_text = []
    text_dict = {}
    for i in range(n_boxes):
        if int(d['conf'][i]) > -1:  # Adjust confidence threshold
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            # expand
            x = max(x - 5 - 5, 0)
            y = max(y - 5 - 5, 0)
            w = w + 10 + 10
            h = h + 10 + 10

            # rectangle
            box_img = cv2.rectangle(box_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # crop
            crop = img[y:y + h, x:x + w]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
            _, crop = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
            crop = scale_img(crop, 150)

            text = pytesseract.image_to_string(crop, config='--psm 6')# -c tessedit_char_whitelist="0123456789/"')
            
            if (len(text) > 5):
                text_dict[i] = text[:-1]
    

    target = "Kills / Assists / Knocks"
    similarities = [(key, val, str_similarity(val, target)) for key, val in text_dict.items()]
    top3_similarities = sorted(similarities, key=lambda x: x[2], reverse=True)[:3]
    top3_similarities = sorted(top3_similarities, key=lambda x:x[0], reverse=False)

    kak_img = img.copy()
    all_h = []
    all_y = []
    all_w = []
    ## get the boxes on KAK from target boxes
    for item in top3_similarities:
        all_h.append(d['height'][item[0]])
        all_y.append(d['top'][item[0]])
        all_w.append(d['width'][item[0]])

    ideal_h = min(all_h)
    ideal_y = max(all_y)
    ideal_w = min(all_w)

    # print('h: ', ideal_h)
    # print('w: ', ideal_w)
    # print('ratio: ', ideal_h/ideal_w)
    if ideal_h / ideal_w > .10:
        cut = int((ideal_h - (ideal_w * .10)) / 2)
        ideal_y += cut
        ideal_h -= cut

    for idx, item in enumerate(top3_similarities):
        # all_h.append(d['height'][item[0]])
        (x, y, w, h) = (d['left'][item[0]], d['top'][item[0]], d['width'][item[0]], d['height'][item[0]])

        all_h.append(h)
        x = x-10
        y = ideal_y+17
        w = ideal_w
        h = ideal_h + 20

        # rectangle
        # kak_img = cv2.rectangle(kak_img, (x, y), (x + w, y + h), (0, 255, 0), 2) # G 
        # kak_img = cv2.rectangle(kak_img, (x, ideal_y), (x + ideal_w, ideal_y + ideal_h), (255, 0, 0), 2) # B

        # crop
        crop = img[y:y + h, x:x + w]

        fname = f'KAK_crops_temp/crop{idx}.jpg'
        cv2.imwrite(fname, crop)

        ### CALL CROP READER

def find_vertical_lines(arr):
    max_val = max(arr)
    bin_arr = []
    flag = True
    sub_bin_arr = []
    for idx , val in enumerate(arr):
        if val == max_val:
            if flag:
                sub_bin_arr.append(idx)
            else:
                sub_bin_arr = []
                sub_bin_arr.append(idx)
                flag = True
        else:
            if flag:
                bin_arr.append(sub_bin_arr)
                flag = False
    bin_arr.append(sub_bin_arr)


    var_lines = bin_arr[1:5]
    out = [0]
    for arr in var_lines:
        out.append(int(sum(arr) / len(arr)))
    
    out.append(out[-1] + 30)

    return out

def read_KAK_crops(img_file):
    img = cv2.imread(img_file, cv2.IMREAD_GRAYSCALE)
    img=img[5::, 0::]
    img=scale_img(img, 150)
    cv2.imwrite('gray.jpg', img)

    _, binary_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    # cv2.imwrite('bin_img.jpg', binary_img)

    column_sums = np.sum(binary_img, axis=0)
    row_sums=np.sum(binary_img, axis=1)

    cols=find_vertical_lines(column_sums)
    # print(cols)

    str=''

    for i in range(len(cols)-1):
        crop_test = img[0::, cols[i]:cols[i+1]]
        cv2.imwrite('KAK_crops_char/char0.jpg', crop_test)
        char = pytesseract.image_to_string(crop_test, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')[:1]
        
        if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '/']:
            # print('char not indentified...!')
            char = pytesseract.image_to_string(crop_test, config='--psm 6 -c tessedit_char_whitelist="0123456789/"')[:1]
            if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '/']:
                char = pytesseract.image_to_string(crop_test, config='--psm 8 -c tessedit_char_whitelist="0123456789/"')[:1]
                if char not in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '/']:
                    char = '_'
        
        str += char
            # print('char found : ', i)

    # print('KAK: ', str)
    return str


### Helpers
def scale_img(img, pct):
    scale_percent = pct
    width = int(img.shape[1] * pct / 100)
    height = int(img.shape[0] * pct / 100)
    dim = (width, height)
    rs_image = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
    
    return rs_image

def str_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()
        

def main():
    """Main function to process Apex Legends OCR."""
    parser = argparse.ArgumentParser(description="Apex Legends OCR Processing")
    parser.add_argument("-f", "--filename", type=str, required=True, help="Path to the scoreboard image file")
    
    args = parser.parse_args()
    img_file = args.filename

    if not os.path.exists(img_file):
        print(json.dumps({"error": f"File not found: {img_file}"}))
        return

    # Run the Apex OCR function
    ocr_result = apex_OCR(img_file)

    # Output JSON to stdout (so Flask can capture it)
    print(json.dumps(ocr_result, indent=4))

if __name__ == "__main__":
    main()