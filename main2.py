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



# print(apex_OCR('apex_ss/1.png'))
print(apex_OCR('apex_ss/6.png'))



# Load the image in grayscale
# image_path = "KAK_crops_temp/crop2.jpg"
# img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
# img=img[5::, 0::]
# img=scale_img(img, 150)
# cv2.imwrite('gray.jpg', img)

# # Convert to binary using Otsu’s thresholding
# _, binary_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
# cv2.imwrite('bin_img.jpg', binary_img)
# # Show the binary image
# # plt.imshow(binary_img, cmap='gray')
# # plt.title("Binary Image")
# # plt.show()

# # Compute vertical sum projection (sum of white pixels in each column)
# column_sums = np.sum(binary_img, axis=0)
# row_sums=np.sum(binary_img, axis=1)

# # Find 4 largest black vertical gaps (smallest white pixel sums)
# # gap_indices = np.argsort(column_sums)[:4]  # Get 4 smallest column sums
# # gap_indices = np.sort(gap_indices)  # Sort indices for slicing

# # Plot vertical projection to visualize gaps
# # plt.figure(figsize=(10, 4))
# # plt.plot(column_sums)
# # plt.scatter(gap_indices, column_sums[gap_indices], color='red', label='Detected Gaps')
# # plt.title("Vertical Projection Profile")
# # plt.legend()
# # plt.show()

# cols=find_vertical_lines(column_sums)
# print(cols)

# str=''

# crop_test = img[0::, 0:cols[0]]
# cv2.imwrite('KAK_crops_char/char0.jpg', crop_test)
# str += pytesseract.image_to_string(crop_test, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')[:1]

# crop_test = img[0::, cols[0]:cols[1]]
# cv2.imwrite('KAK_crops_char/char1.jpg', crop_test)
# str += pytesseract.image_to_string(crop_test, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')[:1]

# crop_test = img[0::, cols[1]:cols[2]]
# cv2.imwrite('KAK_crops_char/char2.jpg', crop_test)
# str += pytesseract.image_to_string(crop_test, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')[:1]

# crop_test = img[0::, cols[2]:cols[3]]
# cv2.imwrite('KAK_crops_char/char3.jpg', crop_test)
# str += pytesseract.image_to_string(crop_test, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')[:1]

# crop_test = img[0::, cols[3]-2:cols[3]+30]
# cv2.imwrite('KAK_crops_char/char4.jpg', crop_test)
# str += pytesseract.image_to_string(crop_test, config='--psm 7 -c tessedit_char_whitelist="0123456789/"')[:1]

# print(str)
# # cv2.imshow('cr',crop_test)
# # cv2.waitKey(0)

