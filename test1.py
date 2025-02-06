import cv2
import numpy as np
from PIL import Image
 
import pytesseract
#pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

img = cv2.imread('Apex_Scoreboard1.png', cv2.IMREAD_GRAYSCALE)
# Apply Otsu's thresholding
ret, thresh = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)



# Display the image
thresh = cv2.bitwise_not(thresh)
cv2.imshow('Otsu Thresholding', thresh)
print(pytesseract.image_to_string(thresh))
cv2.waitKey(0)
cv2.destroyAllWindows()