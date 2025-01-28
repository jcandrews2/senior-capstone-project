# import cv2
# import pytesseract
# from pytesseract import Output
# import numpy as np

# def preprocess_image(image_path):
#     """
#     Preprocess the image for better OCR detection.
#     """
#     # Load the image
#     img = cv2.imread(image_path)

#     # Convert to grayscale
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Apply adaptive thresholding
#     processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

#     return processed

# def extract_kills_assists_knocks(img, debug=False):
#     """
#     Extract the "Kills/Assists/Knocks" statistics using pytesseract.
#     """
#     # Run pytesseract on the preprocessed image
#     d = pytesseract.image_to_data(img, output_type=Output.DICT)

#     results = []
#     n_boxes = len(d['text'])
#     print('num boxes: ', n_boxes)
#     for i in range(n_boxes):
#         # Find text with "Kills / Assists / Knocks" in it
#         if "kills" in d['text'][i].lower() or "/" in d['text'][i]:
#             # Extract surrounding text (e.g., numbers near it)
#             x, y, w, h = d['left'][i], d['top'][i], d['width'][i], d['height'][i]
#             crop_img = img[y:y+h, x:x+w]

#             # OCR on the cropped image
#             text = pytesseract.image_to_string(crop_img, config="--psm 7")
#             results.append(text)

#             if debug:
#                 # Draw a rectangle and display for debugging
#                 img_with_box = cv2.rectangle(img.copy(), (x, y), (x + w, y + h), (0, 255, 0), 2)
#                 cv2.imshow("Debug", img_with_box)
#                 cv2.waitKey(0)

#     return results

# def main(image_path):
#     # Preprocess the image
#     preprocessed_img = preprocess_image(image_path)

#     # Extract statistics
#     stats = extract_kills_assists_knocks(preprocessed_img, debug=True)

#     # Print results
#     print("Extracted Stats:")
#     for stat in stats:
#         print(stat)

# if __name__ == "__main__":
#     image_path = "image_data/apex.png"  # Path to your image
#     main(image_path)
