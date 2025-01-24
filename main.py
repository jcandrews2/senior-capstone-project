import cv2
from pytesseract import pytesseract, Output
from ApexFuncs import *

img = cv2.imread('image_data/apex.png')
# img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# img = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

#### BOX FOR EACH CHAR
# h, w, c = img.shape
# boxes = pytesseract.image_to_boxes(img) 
# for b in boxes.splitlines():
#     b = b.split(' ')
#     img = cv2.rectangle(img, (int(b[1]), h - int(b[2])), (int(b[3]), h - int(b[4])), (0, 255, 0), 2)

# cv2.imshow('img', img)
# cv2.waitKey(0)


#### BOX FOR EACH TEXT BLOCK
# d = pytesseract.image_to_data(img, output_type=Output.DICT)
# print(d.keys())

# n_boxes = len(d['text'])
# for i in range(n_boxes):
#     if int(d['conf'][i]) > 60:
#         (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
#         img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

# cv2.imshow('img', img)
# cv2.waitKey(0)




# d = pytesseract.image_to_data(img, output_type=Output.DICT)

# n_boxes = len(d['text'])
# for i in range(n_boxes):
#     # confidence > 60
#     if int(d['conf'][i]) > 60:
#         #box coordinates
#         (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])

#         # extend box
#         x = max(x - 5, 0)
#         y = max(y - 5, 0)
#         w = w + 10
#         h = h + 10

#         img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

#         # crop
#         crop = img[y:y + h, x:x + w]
#         text = pytesseract.image_to_string(crop, config='--psm 6')
#         print(f"Detected text in box {i}: {text.strip()}")

# cv2.imwrite('boxed_im.jpg', img)

# cv2.imshow('Detected Boxes', img)
# cv2.waitKey(0)
# cv2.destroyAllWindows()







# IMG -> GRAYSCALE: good for "damage dealt" score on Apex
# IMG: good for "kills/assists/knocks" on Apex

# grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 15, -2)

# thresholding
# _, processed_img = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)  # Not good for Apex

# # Optionally apply dilation for better text detection
# kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
# processed_img = cv2.dilate(binary, kernel, iterations=1)

# OCR to get bounding boxes
d = pytesseract.image_to_data(gray, output_type=Output.DICT, lang='eng', config='--psm 6 -c tessedit_char_whitelist="0123456789:/#"') #abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ

# detected boxes
n_boxes = len(d['text'])

for i in range(n_boxes):
    if int(d['conf'][i]) > 0:  # Adjust confidence threshold
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        
        # expand
        x = max(x - 5, 0)
        y = max(y - 5, 0)
        w = w + 10
        h = h + 10

        # rectangle
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # crop
        crop = img[y:y + h, x:x + w]


        text = pytesseract.image_to_string(crop, config='--psm 6 -c tessedit_char_whitelist="0123456789:/#"')
        # print(f"Detected text in box {i}: {text.strip()}")
        print(text)


cv2.imwrite('processed_boxed_image.jpg', img)
cv2.imwrite('input_img.jpg', gray)
cv2.imshow('Detected Boxes', img)
cv2.waitKey(0)
cv2.destroyAllWindows()