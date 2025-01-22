import cv2
import numpy as np
from PIL import Image
import pytesseract
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Read the image
image = cv2.imread('Apex_Scoreboard.png')
# Define the coordinates of the region of interest (ROI)
x, y, w, h = 0, 0, 530, 150
k, l, m, n = 1420, 120, 200, 75
aa, ab, ac, ad, ae = 200, 270, 300, 250, 475

# Crop the image
cropped_image_codeword = image[y:y+h, x:x+w]
cropped_image_placement = image[l:l+n, k:k+m]
cropped_img_p1 = image[ab:ab+ad, aa:aa+ac]
cropped_img_p2 = image[ab:ab+ad, aa+ae:aa+ac+ae]
cropped_img_p3 = image[ab:ab+ad, aa+(2*ae):aa+(2*ae)+ac+150]

cv2.imwrite('codeword.png', cropped_image_codeword)
cv2.imwrite('placement.png', cropped_image_placement)
cv2.imwrite('p1.png', cropped_img_p1)
cv2.imwrite('p2.png', cropped_img_p2)
cv2.imwrite('p3.png', cropped_img_p3)


# Display the cropped image
'''
cv2.imshow('Cropped Image', cropped_image_codeword)
cv2.imshow('Cropped Image', cropped_image_placement)
cv2.imshow('Cropped Image', cropped_img_p1)
cv2.imshow('Cropped Image', cropped_img_p2)
cv2.imshow('Cropped Image', cropped_img_p3)
'''

config = '--psm 6 -c tessedit_char_whitelist="abcdefghijklmnopqrstuvwxyz"'
img0 = cv2.imread('codeword.png', cv2.IMREAD_GRAYSCALE)
ret, thresh0 = cv2.threshold(img0, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh0 = cv2.bitwise_not(thresh0)
print(pytesseract.image_to_string(thresh0))


config = '--psm 6 -c tessedit_char_whitelist="0123456789"'
img1 = cv2.imread('placement.png', cv2.IMREAD_GRAYSCALE)
ret, thresh1 = cv2.threshold(img1, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh1 = cv2.bitwise_not(thresh1)
print(pytesseract.image_to_string(thresh1))

img2 = cv2.imread('p1.png', cv2.IMREAD_GRAYSCALE)
ret, thresh2 = cv2.threshold(img2, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh1 = cv2.bitwise_not(thresh2)
print(pytesseract.image_to_string(thresh2))

img3 = cv2.imread('p2.png', cv2.IMREAD_GRAYSCALE)
ret, thresh3 = cv2.threshold(img3, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh1 = cv2.bitwise_not(thresh3)
print(pytesseract.image_to_string(thresh3))

img4 = cv2.imread('p3.png', cv2.IMREAD_GRAYSCALE)
ret, thresh4 = cv2.threshold(img4, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
thresh4 = cv2.bitwise_not(thresh4)
print(pytesseract.image_to_string(thresh4))

cv2.waitKey(0)
cv2.destroyAllWindows()