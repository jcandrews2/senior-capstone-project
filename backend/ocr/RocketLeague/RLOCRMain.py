import cv2 as cv
import numpy as np
from collections import defaultdict
import json
import os
import pytesseract
import argparse
import sys

#UPLOAD REQUIREMENTS:
#1. 1920 x 1080 resolution
#2. 16:9 aspect ratio
#3. Final Scoreboard Postgame Only
#4. No overlays (Discord, Outplayed, etc.)
#5. Winning Team is responisble for uploading screenshots
#6. If abnormal data is detected (e.g. 0 Score, etc.), uploader will be required to verify the data

def main():
    #pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract'
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


    parser = argparse.ArgumentParser(
                        prog='Rocket League OCR',
                        description='Intakes a screenshot of a Rocket League scoreboard and performs OCR to extract player data.',
                        epilog='1920x1080 resolution, 16:9 aspect ratio required. .png or .jpg format only.')
    #Load screenshot
    parser.add_argument('-f', '--filename', type=str, required=True, help='Path to the screenshot file.')
    args = parser.parse_args()
    img_path = args.filename

    if os.path.exists(img_path):
        #print(f"File {img_path} found.")
        pass
    else:
        print(f"File {img_path} not found.")

    img_rgb = cv.imread(img_path)
    if img_rgb is None:
        print(f"Error: Failed to load image {img_path}.")

    img_rgb = cv.resize(img_rgb, (1920, 1080))
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    #                              Score,Goals,Assists,Saves,Shots
    players = defaultdict(lambda: ('0', '0', '0', '0', '0'))

    #Define the region of interest (ROI)
    x, y, w, h = 670, 280, 925, 420
    roi_gray = img_gray[y:y+h, x:x+w]
    #cv.imshow(f'ROI', roi_gray)
    #cv.waitKey(0)
    roi_gray = cv.Canny(roi_gray, 50, 150)


    for i in range(6):
    #Define ROI for OCR
        strip_x =  67
        if i == 0:
            strip_y = 10
        if i == 3:
            strip_y = 58 * i + 90
        elif i > 3:
            strip_y =  58 * i + 90
        else:
            strip_y = 60 * i
        strip_w = 843
        strip_h = 45
        strip = roi_gray[strip_y:strip_y + strip_h, strip_x:strip_x + strip_w]
        #cv.imshow(f'OCR ROI', strip)
        #cv.waitKey(0)

        strip_gray = cv.adaptiveThreshold(
        strip, 
        255,
        cv.ADAPTIVE_THRESH_MEAN_C, 
        cv.THRESH_BINARY, 
        7, 
        -2
    )
        #strip_gray = cv.GaussianBlur(strip_gray, (5, 5), 0)
        strip_gray = cv.Canny(strip_gray, 50, 150)


        strip_name = strip_gray[:35, :300]
        strip_stats = strip_gray[5:, 390:]
        strip_score = strip_stats[5:, :100]
        strip_goals = strip_stats[5:, 115:175]
        strip_assists = strip_stats[5:, 200:275]
        strip_saves = strip_stats[5:, 320:380]
        strip_shots = strip_stats[5:, 410:]


        strips = [strip_name, strip_score, strip_goals, strip_assists, strip_saves, strip_shots]

        for s in strips:
            s = cv.resize(s, None, fx=5, fy=5, interpolation=cv.INTER_LINEAR)
            s = cv.adaptiveThreshold(
            s, 
            255,
            cv.ADAPTIVE_THRESH_MEAN_C, 
            cv.THRESH_BINARY, 
            7, 
            -2
    )   
            s = cv.Canny(s, 50, 150)

        #Set OCR configurations
        config0 = '--psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        config1 = '--psm 8 -c tessedit_char_whitelist=0123456789'
        #cv.imshow(f'Strip Name {i}', strip_name)
        #cv.waitKey(0)

        #Perform OCR
        ocr_name = pytesseract.image_to_string(strip_name, config=config0)
        ocr_score = pytesseract.image_to_string(strip_score, config=config1)
        ocr_goals = pytesseract.image_to_string(strip_goals, config=config1)
        ocr_assists = pytesseract.image_to_string(strip_assists, config=config1)
        ocr_saves = pytesseract.image_to_string(strip_saves, config=config1)
        ocr_shots = pytesseract.image_to_string(strip_shots, config=config1)
        #Update player stats, using 0 if not found
        current_score, current_goals, current_assists, current_saves, current_shots = players.get(ocr_name.split(' ')[0], ('0', '0', '0', '0', '0'))
        if ocr_score.strip() or ocr_score.strip() == '0':
            current_score = ocr_score.strip()
        if ocr_goals.strip() or ocr_goals.strip() == '0':
            current_goals = ocr_goals.strip()
        if ocr_assists.strip() or ocr_assists.strip() == '0':
            current_assists = ocr_assists.strip()
        if ocr_saves.strip() or ocr_saves.strip() == '0':
            current_saves = ocr_saves.strip()
        if ocr_shots.strip() or ocr_shots.strip() == '0':
            current_shots = ocr_shots.strip()
        if not ocr_name:
            ocr_name = f'Unknown Player {i}'
        players[ocr_name] =  current_score, current_goals, current_assists, current_saves, current_shots

        
        """print(f"OCR Score: {ocr_score}")
        print(f"OCR Goals: {ocr_goals}")
        print(f"OCR Assists: {ocr_assists}")
        print(f"OCR Saves: {ocr_saves}")
        print(f"OCR Shots: {ocr_shots}") """

        img_result = img_rgb.copy()


        #Draw rectangles and text on the result image
        cv.putText(img_result, f"{ocr_name.split(' ')[0]}", (strip_x, strip_y + 40*i), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Score: {current_score.strip()}', (strip_x + 2900, strip_y+ 40*i), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Goals: {current_goals.strip()}', (strip_x + 380, strip_y+ 40*i), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Assists: {current_assists.strip()}', (strip_x + 460, strip_y+ 40*i), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Saves: {current_saves.strip()}', (strip_x + 520, strip_y+ 40*i), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Shots: {current_shots.strip()}', (strip_x + 600, strip_y+ 40*i), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)


    #Save result
    output_path = f'scoreboard_result{args.filename}'
    #cv.imshow('Result', img_result)
    #cv.waitKey(0)
    cv.imwrite(output_path, img_result)

    #Convert players dictionary into a single JSON structure
    players = dict(players)

    #Create JSON output directory if doesn't
    json_output_dir = 'JSON'
    os.makedirs(json_output_dir, exist_ok=True)

    #Write JSON to file
    json_output_path = os.path.join(json_output_dir, f'players_{args.filename.replace(".png","")}.json')
    json_output_path = json_output_path.replace(".jpg", "")

    with open(json_output_path, 'w') as json_file:
        json.dump(players, json_file, indent=4)
    sys.stdout.write(json.dumps(players)) #Ensures only the JSON result is sent to stdout
    return json_file

if __name__ == '__main__':
    main()