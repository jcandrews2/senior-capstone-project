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
#2. 16:9 aspect ratio, .png or .jpg format only
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

    img_rgb = cv.imread(img_path)

    img_rgb = cv.resize(img_rgb, (1920, 1080))
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    #                              Score,Goals,Assists,Saves,Shots
    players = defaultdict(lambda: ('0', '0', '0', '0', '0'))

    #Define the region of interest (ROI)
    x, y, w, h = 670, 280, 925, 420
    roi_gray = img_gray[y:y+h, x:x+w]
    roi_gray = cv.Canny(roi_gray, 50, 150)
    img_result = img_rgb.copy()
    for i in range(6):
    #Define ROI for OCR
        strip_x =  67
        if i == 0:
            strip_y = 10
        if i == 3:
            strip_y = 58 * i + 86
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
        11, 
        -2
    )
        fx = 7
        fy = 7
        strip_name = strip_gray[:35, :300]
        #cv.imshow("NAME", strip_name)
        #cv.waitKey(0)
        strip_stats = strip_gray[5:, 390:]
        strip_score = cv.resize(strip_stats[5:, :100], (0,0), fx=fx, fy=fy)
        #cv.imshow("SCORE", strip_score)
        #cv.waitKey(0)
        strip_goals = cv.resize(strip_stats[5:, 115:175], (0,0), fx=fx, fy=fy)
        #cv.imshow("GOALS", strip_goals)
        #cv.waitKey(0)
        strip_assists = cv.resize(strip_stats[5:, 200:275], (0,0), fx=fx, fy=fy)
        #cv.imshow("ASSISTS", strip_assists)
        #cv.waitKey(0)
        strip_saves = cv.resize(strip_stats[5:, 320:380], (0,0), fx=fx, fy=fy)
        #cv.imshow("SAVES", strip_saves)
        #cv.waitKey(0)
        strip_shots = cv.resize(strip_stats[5:, 410:], (0,0), fx=fx, fy=fy)
        #cv.imshow("SHOTS", strip_shots)
        #cv.waitKey(0)




        #Set OCR configurations
        config0 = '--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        config1 = '--psm 8 -c tessedit_char_whitelist=0123456789'
        config2 = '--psm 10 -c tessedit_char_whitelist=0123456789'
        #cv.imshow(f'Strip Name {i}', strip_name)
        #cv.waitKey(0)

        #Perform OCR
        ocr_name = pytesseract.image_to_string(strip_name, config=config0).replace('\n', '')
        ocr_score = pytesseract.image_to_string(strip_score, config=config1)
        ocr_goals = pytesseract.image_to_string(strip_goals, config=config2)
        ocr_assists = pytesseract.image_to_string(strip_assists, config=config2)
        ocr_saves = pytesseract.image_to_string(strip_saves, config=config2)
        ocr_shots = pytesseract.image_to_string(strip_shots, config=config2)
        #Update player stats, using -1 if not found
        current_score, current_goals, current_assists, current_saves, current_shots = players.get(ocr_name.split(' ')[0], ('-1', '-1', '-1', '-1', '-1'))
        if ocr_score or ocr_score == '0':
            current_score = ocr_score.strip()
        if ocr_goals or ocr_goals == '0':
            current_goals = ocr_goals.strip()
        if ocr_assists or ocr_assists == '0':
            current_assists = ocr_assists.strip()
        if ocr_saves or ocr_saves == '0':
            current_saves = ocr_saves.strip()
        if ocr_shots or ocr_shots == '0':
            current_shots = ocr_shots.strip()
        if not ocr_name:
            ocr_name = f'Unknown Player {i}'
        players[ocr_name] =  current_score, current_goals, current_assists, current_saves, current_shots



        #Draw rectangles and text on the result image
        cv.putText(img_result, f"{ocr_name}", (strip_x + 450, strip_y + 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv.putText(img_result, f'Score: {current_score.strip()}', (strip_x + 950, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv.putText(img_result, f'Goals: {current_goals.strip()}', (strip_x + 1130, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv.putText(img_result, f'Assists: {current_assists.strip()}', (strip_x + 1260, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv.putText(img_result, f'Saves: {current_saves.strip()}', (strip_x + 1370, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        cv.putText(img_result, f'Shots: {current_shots.strip()}', (strip_x + 1500, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


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