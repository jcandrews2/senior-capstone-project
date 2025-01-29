from ApexFuncs import *
from funcs import scale_img
import cv2
from PIL import Image, ImageEnhance, ImageFilter

# print(get_damage_dealt('apex_ss/2.png'))
# print(get_KAK_simple('image_data/apex.png'))

# img = cv2.imread('KAK_crops_temp/crop_sample17.png')
# x = get_char_boxes(img)

# print('here: \n', x)


# print(get_KAK('image_data/apex.png'))

# print('PNG #1: ', get_KAK('apex_ss/1.png', 1))
# print('PNG #2: ', get_KAK('apex_ss/2.png',2))
# print('PNG #3: ', get_KAK('apex_ss/3.png',3))
# print('PNG #4: ', get_KAK('apex_ss/4.png',4))
# print('PNG #5: ', get_KAK('apex_ss/5.png',5))
# print('PNG #6: ', get_KAK('apex_ss/6.png',6))


# cust_congf = '--oem 3 --psm 6 -c tessedit_char_whitelist="0123456789/"'
print(get_char_boxes(cv2.imread('KAK_crops_temp/crop1.jpg')))

# print(pytesseract.image_to_string(cv2.imread('KAK_crops_temp/crop2.jpg'), config=cust_congf))


# # image = cv2.imread('KAK_crops_temp/crop0.jpg')
# image = Image.open('processed_crop1.jpg')
# image = image.convert("L")  # Convert to grayscale
# image = image.filter(ImageFilter.SHARPEN)  # Sharpen the image
# image = ImageEnhance.Contrast(image).enhance(2)  # Increase contrast

# # Perform OCR with improved settings
# custom_config = "--psm 7 --oem 3"
# extracted_text = pytesseract.image_to_string(image, config=custom_config)

# # Output cleaned text
# print(extracted_text.strip())