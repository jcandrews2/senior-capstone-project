from ApexFuncs import *
from funcs import scale_img
import cv2

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


im = cv2.imread('KAK_crops_temp/crop1.jpg')
cv2.imshow('im', im)
cv2.waitKey(0)
# d = pytesseract.image_to_data(cv2.imread('KAK_crops_temp/crop0.jpg'), output_type=Output.DICT)

# print(apex_OCR(cv2.imread('KAK_crops_temp/crop0.jpg')))