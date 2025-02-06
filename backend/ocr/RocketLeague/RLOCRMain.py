import cv2 as cv
import numpy as np
from collections import defaultdict
import json
import os
import pytesseract
import argparse
import sys

def load_and_preprocess_image(img_path):
    """Load and preprocess the image."""
    img_rgb = cv.imread(img_path)
    img_rgb = cv.resize(img_rgb, (1920, 1080))
    img_gray = cv.cvtColor(img_rgb, cv.COLOR_BGR2GRAY)
    #clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(3, 3))
    #img_gray = clahe.apply(img_gray)
    return img_rgb, img_gray


def classify_scoreboard(image, roi_x, roi_y, roi_w, roi_h, threshold=10):
    """Classify the scoreboard based on the darkness of the post-game chat"""

    roi = image[roi_y:roi_y + roi_h, roi_x:roi_x + roi_w]
    #cv.imshow("Timer?", roi)
    #cv.waitKey(0)

    average_intensity = np.mean(roi)
    print(average_intensity)

    if average_intensity > threshold:
        print("Replay")
        return "Replay"
    else:
        print("Post")
        return "Post"

def extract_roi(img_gray, x, y, w, h):
    """Extract the region of interest (ROI) from the image."""
    roi_gray = img_gray[y:y+h, x:x+w]
    #roi_gray_name = cv.Canny(roi_gray, 50, 150)
    return roi_gray, roi_gray

def open_strip(strip):
    """Perform a morphological opening on each strip"""
    kernel = np.ones(3, np.uint8)
    strip = cv.resize(strip, (0,0), fx=5, fy=5)
    strip = cv.erode(strip, kernel=kernel, iterations=4)
    #strip = cv.dilate(strip, kernel=kernel)
    return strip

def process_strip(strip_gray, strip_n, strip_y, strip_h, strip_x, strip_w, scoreboard_type):
    """Process each strip (player's stats) within the ROI."""
    strip_gray = cv.GaussianBlur(strip_gray, (3,3), 0)
    _, strip_gray = cv.threshold(strip_gray, 0, 255, cv.THRESH_BINARY + cv.THRESH_OTSU)
    if scoreboard_type == "Post":
        strip_name = strip_n[:27, :290]
        #cv.imshow("Name", strip_name)
        strip_stats = strip_gray[:, 330:]
        #cv.imshow("Stats", strip_stats)
        #cv.waitKey(0)
        strip_score = open_strip(strip_stats[:, :65])
        #cv.imshow("Score", strip_score)
        strip_goals = open_strip(strip_stats[:, 95:150])
        #cv.imshow("Goals", strip_goals)
        strip_assists = open_strip(strip_stats[:, 185:230])
        #cv.imshow("Assists", strip_assists)
        strip_saves = open_strip(strip_stats[:, 275:320])
        #cv.imshow("Saves", strip_saves)
        strip_shots = open_strip(strip_stats[:, 360:])
        #cv.imshow("Shots", strip_shots)
        #cv.waitKey(0)
    else:
        strip_name = strip_n[:27, :290]
        #cv.imshow("Name", strip_name)
        strip_stats = strip_gray[:, 305:]
        #cv.imshow("Stats", strip_stats)
        #cv.waitKey(0)
        strip_score = open_strip(strip_stats[:, :65])
        #cv.imshow("Score", strip_score)
        strip_goals = open_strip(strip_stats[:, 95:145])
        #cv.imshow("Goals", strip_goals)
        strip_assists = open_strip(strip_stats[:, 180:230])
        #cv.imshow("Assists", strip_assists)
        strip_saves = open_strip(strip_stats[:, 270:320])
        #cv.imshow("Saves", strip_saves)
        strip_shots = open_strip(strip_stats[:, 360:])
        #cv.imshow("Shots", strip_shots)
        #cv.waitKey(0)
    return strip_name, strip_score, strip_goals, strip_assists, strip_saves, strip_shots

def perform_ocr(strip, config):
    """Perform OCR on the given image strip."""
    #cv.imshow("", strip)
    #cv.waitKey(0)
    return pytesseract.image_to_string(strip, config=config).strip()

def update_player_stats(players, ocr_name, ocr_score, ocr_goals, ocr_assists, ocr_saves, ocr_shots, i):
    """Update the player's stats in the dictionary."""
    current_score, current_goals, current_assists, current_saves, current_shots = players.get(ocr_name.split(' ')[0], ('0', '0', '0', '0', '0'))
    if not ocr_name.strip:
        return players
    if ocr_score != '' or ocr_score == '0':
        #print(f'Score:', ocr_score)
        current_score = ocr_score
    if ocr_goals != '' or ocr_goals == '0':
        #print(f'Goals:', ocr_goals)
        current_goals = ocr_goals
    if ocr_assists != '' or ocr_assists == '0':
        #print(f'Assists:',ocr_assists)
        current_assists = ocr_assists
    if ocr_saves != '' or ocr_saves == '0':
        current_saves = ocr_saves
    if ocr_shots != '' or ocr_shots == '0':
        current_shots = ocr_shots
    if not ocr_name:
        ocr_name = f'Unknown Player {i+1}'
    players[ocr_name] = current_score, current_goals, current_assists, current_saves, current_shots
    return players

def draw_results(img_result, strip_x, strip_y, i, ocr_name, current_score, current_goals, current_assists, current_saves, current_shots):
    """Draw the results on the image."""
    cv.putText(img_result, f"{ocr_name}", (strip_x + 450, strip_y + 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv.putText(img_result, f'Score: {current_score}', (strip_x + 950, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv.putText(img_result, f'Goals: {current_goals}', (strip_x + 1130, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv.putText(img_result, f'Assists: {current_assists}', (strip_x + 1260, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv.putText(img_result, f'Saves: {current_saves}', (strip_x + 1370, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    cv.putText(img_result, f'Shots: {current_shots}', (strip_x + 1500, strip_y+ 20*i + 200), cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

def save_results(img_result, players, filename):
    """Save the results (image and JSON)."""
    output_path = f'scoreboard_result{filename}'
    cv.imwrite(output_path, img_result)

    players = dict(players)
    json_output_dir = 'JSON'
    os.makedirs(json_output_dir, exist_ok=True)

    json_output_path = os.path.join(json_output_dir, f'players_{filename.replace(".png","")}.json')
    json_output_path = json_output_path.replace(".jpg", "")

    with open(json_output_path, 'w') as json_file:
        json.dump(players, json_file, indent=4)
    sys.stdout.write(json.dumps(players))
    return json_file

def main():
    #usr for vm, homebrew for mac, program files for Windows
    #pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # For VM
    #pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract' # For Mac
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # For Windows

    parser = argparse.ArgumentParser(
                        prog='Rocket League OCR',
                        description='Intakes a screenshot of a Rocket League scoreboard and performs OCR to extract player data.',
                        epilog='1920x1080 resolution, 16:9 aspect ratio required. .png or .jpg format only.')
    parser.add_argument('-f', '--filename', type=str, required=True, help='Path to the screenshot file.')
    args = parser.parse_args()
    img_path = args.filename

    img_rgb, img_gray = load_and_preprocess_image(img_path)
    players = defaultdict(lambda: ('-1', '-1', '-1', '-1', '-1'))
    roi_x, roi_y, roi_w, roi_h = 330, 70, 120, 150

    # Classify the scoreboard
    scoreboard_type = classify_scoreboard(img_gray, roi_x, roi_y, roi_w, roi_h, threshold=10)

    if scoreboard_type == "Post":
        x, y, w, h = 725, 275, 730, 355
    else:
        x, y, w, h = 590, 377, 710, 360
    roi_gray, roi_gray_n = extract_roi(img_gray, x, y, w, h)
    img_result = img_rgb.copy()

    for i in range(6):
        strip_x = 0
        strip_y = [3, 55, 100, 225, 275, 325][i]
        strip_w = 725
        strip_h = 35
        strip = roi_gray[strip_y:strip_y + strip_h, strip_x:strip_x + strip_w]
        strip_n = roi_gray_n[strip_y:strip_y + 30, strip_x:strip_x + strip_w]
        cv.imshow('', strip)
        cv.waitKey(0)

        strip_name, strip_score, strip_goals, strip_assists, strip_saves, strip_shots = process_strip(strip, strip_n, strip_y, strip_h, strip_x, strip_w, scoreboard_type)

        config0 = '--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        config1 = '--psm 8 -c tessedit_char_whitelist=0123456789'
        config2 = '--psm 8 -c tessedit_char_whitelist=0123456789'

        ocr_name = perform_ocr(strip_name, config0)
        ocr_score = perform_ocr(strip_score, config1)
        ocr_goals = perform_ocr(strip_goals, config2)
        ocr_assists = perform_ocr(strip_assists, config2)
        #print(f'Assists for', {ocr_name},':', {ocr_assists})
        ocr_saves = perform_ocr(strip_saves, config2)
        ocr_shots = perform_ocr(strip_shots, config2)

        #print(ocr_name, ocr_score, ocr_goals, ocr_assists, ocr_saves, ocr_shots)

        players = update_player_stats(players, ocr_name, ocr_score, ocr_goals, ocr_assists, ocr_saves, ocr_shots, i)
        draw_results(img_result, strip_x, strip_y, i, ocr_name, *players[ocr_name])

    save_results(img_result, players, args.filename)

if __name__ == '__main__':
    main()