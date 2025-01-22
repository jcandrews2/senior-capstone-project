import cv2
import numpy as np
from PIL import Image, ImageOps
import pytesseract

'''pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'''

#reads image and makse it grayscale
img = cv2.imread('Val_Scoreboard.png', cv2.IMREAD_GRAYSCALE)

#inverts image
#works best if using regular
img = ~img

def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)

def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)


def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

'''img = erode(dilate(img))'''

#displays image
cv2.imshow('Image', img)

#whitelists the characters
config = '--psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/"'

#prints what we get from the image
text = pytesseract.image_to_string(img, config=config)
print(text.replace('\n', '').replace('\f', ''))

#lets us see the image
cv2.waitKey(0)
cv2.destroyAllWindows()