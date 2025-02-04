from ApexFuncs import *
import cv2
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np
import matplotlib.pyplot as plt


# print(get_damage_dealt('apex_ss/2.png'))
# print(get_KAK_simple('image_data/apex.png'))

# img = cv2.imread('KAK_crops_temp/crop_sample17.png')
# x = get_char_boxes(img)

# print('here: \n', x)


# print(get_KAK('image_data/apex.png'))

# print('PNG #1: ', get_KAK_crops('apex_ss/1.png'))
# print('PNG #2: ', get_KAK_crops('apex_ss/2.png'))
# print('PNG #3: ', get_KAK_crops('apex_ss/3.png'))
# print('PNG #4: ', get_KAK_crops('apex_ss/4.png'))
# print('PNG #5: ', get_KAK_crops('apex_ss/5.png'))
# print('PNG #6: ', get_KAK_crops('apex_ss/6.png'))



print(apex_OCR('apex_ss/1.png'))
# print(apex_OCR('apex_ss/6.png'))