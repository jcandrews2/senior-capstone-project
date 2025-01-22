# Libraries
from PIL import Image
import cv2
import pytesseract

print('x')

im = cv2.imread('image_data/apex.png')
cv2.imshow("Thresholded Image", im)
cv2.waitKey(0)
cv2.destroyAllWindows()