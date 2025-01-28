import cv2
from pytesseract import pytesseract, Output
from funcs import *
import os
import glob

def apex_OCR(img_file):
    out = {"code" : 'AC',
           "squad_placed" : "0",
           "players" : [
               {
                    "name" : 'x0',
                    "kak" : '0/0/0',
                    "damage" : "000",
               },
               {
                    "name" : 'x1',
                    "kak" : '1/1/1',
                    "damage" : "111",
               },
               {
                    "name" : 'x2',
                    "kak" : '2/2/2',
                    "damage" : "222",
               }
           ]}
    return out

def get_damage_dealt(img_file):
    img = cv2.imread(img_file)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    d = pytesseract.image_to_data(gray, output_type=Output.DICT, lang='eng', config='--psm 6 -c tessedit_char_whitelist="0123456789:/#"') #abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

    box_img = img.copy()

    # detected boxes
    n_boxes = len(d['text'])

    all_text = []
    for i in range(n_boxes):
        if int(d['conf'][i]) > 90:  # Adjust confidence threshold
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            
            # expand
            x = max(x - 5, 0)
            y = max(y - 5, 0)
            w = w + 10
            h = h + 10

            # rectangle
            box_img = cv2.rectangle(box_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # crop
            crop = img[y:y + h, x:x + w]
            crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        
            _, binary_image = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
            # res = scale_img(binary_image, 1000)

            text = pytesseract.image_to_string(binary_image, config='--psm 6')#, config='--psm 6 -c tessedit_char_whitelist="0123456789/#ilLI"')
            # print(f"Detected text in box {i}: {text.strip()}")
            if i == 18:
                cv2.imwrite('crop_sample.png', binary_image)
            all_text.append(text[:-1])

    cv2.imwrite('processed_boxed_image.jpg', box_img)
    return list(filter(None, all_text))[:3]


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

    ## get the rect coordinates of the 3 target boxes
    # target_img = img.copy()
    # for item in top3_similarities:
    #     print('target Box #', item[0])
    #     (x, y, w, h) = (d['left'][item[0]], d['top'][item[0]], d['width'][item[0]], d['height'][item[0]])
    #     # expand
    #     # x = max(x - 5 - 5, 0)
    #     # y = max(y - 5 - 5, 0)
    #     # w = w + 10 + 10
    #     # h = h + 10 + 10

    #     # rectangle
    #     target_img = cv2.rectangle(target_img, (x, y), (x + w, y + h), (0, 255, 0), 2)

    kak_img = img.copy()
    all_h = []
    all_y = []
    all_w = []
    ## get the boxes on KAK from target boxes
    for item in top3_similarities:
        all_h.append(d['height'][item[0]])
        all_y.append(d['top'][item[0]])
        all_w.append(d['width'][item[0]])
        # (x, y, w, h) = (d['left'][item[0]], d['top'][item[0]], d['width'][item[0]], d['height'][item[0]])
        # # expand
        # all_h.append(h)
        # x = max(x - 5 - 5, 0)
        # y = max(y - 5 - 5, 0)
        # w = w + 10 + 10
        # h = h + 10 + 10

        # rectangle
        # kak_img = cv2.rectangle(kak_img, (x, (y+h//2)), (x + w, y + h), (0, 255, 0), 2)

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
        crop = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
    
        _, crop = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
        # crop = cv2.medianBlur(crop, 3)
        crop = scale_img(crop, 200)

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



def get_char_boxes(img):
    files = glob.glob('KAK_crops_char/*')
    for f in files:
        os.remove(f)
    # dims
    height, width = img.shape[:2]
    
    # bounding boxes
    d = pytesseract.image_to_boxes(img, output_type=Output.DICT, config='--psm 6 -c tessedit_char_whitelist="0123456789/"')
    n_boxes = len(d['char'])

    whole_txt = ''
    for i in range(n_boxes):
        char = d['char'][i]
        # print('default: ', char)

        x1, y2, x2, y1 = d['left'][i], d['top'][i], d['right'][i], d['bottom'][i]
        
        # adjust for OpenCV (it uses top-left origin)
        y1, y2 = height - y1, height - y2

        # padding
        padding = 10
        x1 = max(x1 - padding, 0)
        y1 = min(y1 + padding, height)
        x2 = min(x2 + padding, width)
        y2 = max(y2 - padding, 0)
        
        # crop
        # crop = img[y2:y1, x1:x2]
        crop = img[y2:y1, x1:x2]

        if (i == 0):
            crop = scale_img(crop,80)
        
        cv2.imwrite(f'KAK_crops_char/char{i}.png', crop)

        text = pytesseract.image_to_string(crop, config='--psm 6 -c tessedit_char_whitelist="0123456789/"')
        print(f'char{i}: ', text)
        whole_txt += text[:1]
        # print(text)
    

    
    return whole_txt
        