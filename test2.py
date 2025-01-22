import cv2
import numpy as np
from PIL import Image
import pytesseract

#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = cv2.imread('Apex_Scoreboard.png', cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img, (0, 0), None, 4.0, 4.0)
img = cv2.threshold(img, 160, 255, cv2.THRESH_BINARY)[1]
config = '--psm 6 -c tessedit_char_whitelist="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/"'
text = pytesseract.image_to_string(img, config=config)
print(text.replace('\n', '').replace('\f', ''))