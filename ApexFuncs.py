import cv2
from pytesseract import pytesseract, Output
from funcs import scale_img

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
def get_KAK(img_file):
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
            res = scale_img(binary_image, 200)

            text = pytesseract.image_to_string(res, config='--psm 6 -c tessedit_char_whitelist="0123456789/"')
            print(f"Detected text in box {i}: {text.strip()}")
            if i == 17 or i == 18 or i == 19:
                cv2.imwrite(f'KAK_crops/crop_sample{i}.png', res)
            

    cv2.imwrite('processed_boxed_image.jpg', box_img)
    return list(filter(None, all_text))


    # cv2.imwrite('processed_boxed_image.jpg', img)
