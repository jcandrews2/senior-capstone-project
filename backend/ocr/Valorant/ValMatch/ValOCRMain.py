import cv2 as cv
import numpy as np
from collections import defaultdict
import re
import json
import os
import pytesseract
import argparse
import sys



#UPLOAD REQUIREMENTS:
#1. 1920 x 1080 resolution
#2. 16:9 aspect ratio
#3. No overlays (Discord, Outplayed, etc.)
#4. Winning Team is responisble for uploading screenshots
#5. If abnormal data is detected (e.g. 0 ACS, 0/0/0 KDA, 0 Econ Rating), uploader will be required to verify the data

def main():
    #usr for vm, homebrew for mac, program files for Windows
    pytesseract.pytesseract.tesseract_cmd = r'/usr/bin/tesseract' # For VM
    #pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/bin/tesseract' # For Mac
    #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe' # For Windows

    parser = argparse.ArgumentParser(
                        prog='Valorant OCR',
                        description='Intakes a screenshot of a Valorant scoreboard and performs OCR to extract player data.',
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
    #                               Agent, ACS, Kills, Deaths, Assists,  Econ,  FB,   P,  D
    players = defaultdict(lambda: ('Agent', '0', '0', '0', '0', '0', '0', '0', '0'))
    img_map = img_gray[115:145, 60:240]
    img_map = cv.adaptiveThreshold(
        img_map, 
        255,
        cv.ADAPTIVE_THRESH_MEAN_C, 
        cv.THRESH_BINARY, 
        3, 
        -2
    )

    img_map = cv.resize(img_map, None, fx=4, fy=4, interpolation=cv.INTER_CUBIC)

    img_score0 = img_gray[80:150, 730:800]
    img_score1 = img_gray[80:150, 1075:1160]

    #Define the region of interest (ROI)
    x, y, w, h = 240, 280, 120, 700
    roi_gray = img_gray[y:y+h, x:x+w]
    roi_rgb = img_rgb[y:y+h, x:x+w]
    #cv.imshow(f'ROI {i}', roi_rgb)
    #cv.waitKey(0)

    #List of agent names
    agents = ["Astra", "Breach", "Brimstone", "Chamber",
            "Clove", "Cypher", "Deadlock", "Fade", "Gekko", "Harbor", "Iso", 
            "Jett", "Killjoy", "KAYO", "Neon", "Omen", "Phoenix", "Raze", 
            "Reyna", "Sage", "Skye", "Sova", "Tejo", "Viper", "Vyse", "Yoru"]

    #List of map names
    maps = ["Abyss", "Ascent", "Bind", "Breeze", "Fracture", "Haven", "Icebox", "Lotus", "Pearl", "Split", "Sunset"]

    #Store detections
    detections = []

    #Preprocess ROI
    #roi_gray = cv.GaussianBlur(roi_gray, (5, 5), 0)
    roi_gray = cv.Canny(roi_gray, 50, 150)

    #Perform template matching for each agent
    for agent in agents:
        template = cv.imread(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ValAgents', f'{agent}.png'), cv.IMREAD_GRAYSCALE)
        if template is None:
            print(f"Template for {agent} not found.")
            continue
        #Apply same filters to templates
        template = cv.GaussianBlur(template, (5, 5), 0)
        template = cv.Canny(template, 50, 150)
        #Attempt multiple scales for matching
        for scale in np.linspace(0.5, 1.5, 10):
            resized_template = cv.resize(template, (0, 0), fx=scale, fy=scale)
            if roi_gray.shape[0] < resized_template.shape[0] or roi_gray.shape[1] < resized_template.shape[1]:
                continue
            res = cv.matchTemplate(roi_gray, resized_template, cv.TM_CCOEFF_NORMED)
            threshold = 0.15
            loc = np.where(res >= threshold)
            for pt in zip(*loc[::-1]):
                score = res[pt[1], pt[0]]
                detected_w, detected_h = resized_template.shape[::-1]
                if detected_w < 60 and detected_w > 45 and detected_h <  60 and detected_h > 45:
                    detections.append((score, agent, (pt[0] + x, pt[1] + y), resized_template.shape[::-1]))

    #Sort detections by score
    detections = sorted(detections, key=lambda x: x[0], reverse=True)

    #Apply non-maximum suppression to filter out overlapping detections
    def non_max_suppression(detections, overlap_thresh=0.05):
        if len(detections) == 0:
            return []

        boxes = np.array([(*pt, pt[0] + w, pt[1] + h) for _, _, pt, (w, h) in detections])
        scores = np.array([score for score, _, _, _ in detections])

        x1 = boxes[:, 0]
        y1 = boxes[:, 1]
        x2 = boxes[:, 2]
        y2 = boxes[:, 3]

        area = (x2 - x1 + 1) * (y2 - y1 + 1)
        idxs = np.argsort(scores)[::-1]

        pick = []
        while len(idxs) > 0:
            i = idxs[0]
            pick.append(i)
            xx1 = np.maximum(x1[i], x1[idxs[1:]])
            yy1 = np.maximum(y1[i], y1[idxs[1:]])
            xx2 = np.minimum(x2[i], x2[idxs[1:]])
            yy2 = np.minimum(y2[i], y2[idxs[1:]])

            w = np.maximum(0, xx2 - xx1 + 1)
            h = np.maximum(0, yy2 - yy1 + 1)

            overlap = (w * h) / area[idxs[1:]]

            idxs = idxs[np.where(overlap <= overlap_thresh)[0] + 1]

        return [detections[i] for i in pick]

    filtered_detections = non_max_suppression(detections)

    #Limit of 2 duplicates per agent
    agent_counts = {}
    final_detections = []
    for detection in filtered_detections:
        _, agent, _, _ = detection
        if agent not in agent_counts:
            agent_counts[agent] = 0
        if agent_counts[agent] < 2:
            final_detections.append(detection)
            agent_counts[agent] += 1


    #print(f"Pre filter: {final_detections}")
    detections_copy = final_detections.copy()
    sum = 0
    cnt = 0
    for _, _, top_left, _ in detections_copy:
        sum += top_left[0]
        cnt += 1
    avg = sum / cnt
    for score, agent, top_left, (w, h) in detections_copy:
        if top_left[0] > np.int64(avg + 5) or top_left[0] < np.int64(avg - 5):
            final_detections.remove((score, agent, top_left, (w, h)))
        
    final_detections = non_max_suppression(final_detections)

    #Ensure no less than 10 detections
    if len(final_detections) < 10:
        remaining_detections = [d for d in detections if d not in final_detections]
        remaining_detections = sorted(remaining_detections, key=lambda x: x[0], reverse=True)
        for detection in remaining_detections:
            _, agent, _, _ = detection
            if agent_counts.get(agent, 0) < 2:
                final_detections.append(detection)
                agent_counts[agent] = agent_counts.get(agent, 0) + 1
            if len(final_detections) == 10:
                break

    #Draw the top 10 matches' rectangles
    final_detections = final_detections[:10]
    #print(f"Post filter: {final_detections}")
    if len(final_detections) != 10:
        print(f"Error: {len(final_detections)} detections found.")

    img_result = img_rgb.copy()
    final_detections = sorted(final_detections, key=lambda x: x[2][1])
    #cv.imshow(f'OCR MAP NAME', img_map)
    #cv.waitKey(0)
    ocr_map = pytesseract.image_to_string(img_map, config='--psm 7 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    #print(f"Map: {ocr_map.strip()}")


    for score, agent, top_left, (w, h) in final_detections:
        current_agent = agent
        bottom_right = (top_left[0] + w, top_left[1] + h)
        cv.rectangle(img_result, top_left, bottom_right, (0, 255, 0), 2)
        cv.putText(img_result, f'{agent} ({score:.2f})', (top_left[0], top_left[1] - 10),
                cv.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        

        #Define ROI for OCR
        strip_x = top_left[0] + w
        strip_y = top_left[1] + 15
        strip_w = 1200
        strip_h = h - 30
        strip = img_rgb[strip_y:strip_y + strip_h, strip_x:strip_x + strip_w]
        #cv.imshow(f'OCR ROI {agent}', strip)
        #cv.waitKey(0)


        strip_gray = cv.cvtColor(strip, cv.COLOR_BGR2GRAY)
        strip_gray = cv.adaptiveThreshold(
        strip_gray, 
        255,
        cv.ADAPTIVE_THRESH_MEAN_C, 
        cv.THRESH_BINARY, 
        3, 
        -2
    )
        #strip_gray = cv.GaussianBlur(strip_gray, (5, 5), 0)
        #strip_gray = cv.Canny(strip_gray, 50, 150)
        #cv.imshow(f'OCR ROI PostProc {agent}', strip_gray)
        #cv.waitKey(0)

        strip_name = strip_gray[:, :200]
        strip_stats = strip_gray[:, 300:]
        strip_acs = strip_stats[:, 70:130]
        strip_kills = strip_stats[:, 200:245]
        strip_deaths = strip_stats[:, 265:295]
        strip_assists = strip_stats[:, 310:355]
        strip_econ = strip_stats[:, 380:500]
        strip_fb = strip_stats[:, 560:620]
        strip_p = strip_stats[:, 700:780]
        strip_d = strip_stats[:, 780:]

        #Set OCR configurations
        config0 = '--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234456789'
        config1 = '--psm 7 -c tessedit_char_whitelist=0123456789'
        config2 = '--psm 7 -c tessedit_char_whitelist=0123456789/'

        #Perform OCR
        ocr_name = pytesseract.image_to_string(strip_gray, config=config0)
        ocr_acs = pytesseract.image_to_string(strip_acs, config=config1)
        ocr_kills = pytesseract.image_to_string(strip_kills, config=config2)
        ocr_deaths = pytesseract.image_to_string(strip_deaths, config=config2)
        ocr_assists = pytesseract.image_to_string(strip_assists, config=config2)
        ocr_econ = pytesseract.image_to_string(strip_econ, config=config1)
        ocr_fb = pytesseract.image_to_string(strip_fb, config=config1)
        ocr_p = pytesseract.image_to_string(strip_p, config=config1)
        ocr_d = pytesseract.image_to_string(strip_d, config=config1)
        ocr_s0 = pytesseract.image_to_string(img_score0, config=config1).replace('\n', '')
        ocr_s1 = pytesseract.image_to_string(img_score1, config=config1).replace('\n', '')
        #print(f"OCR Stats for {ocr_name.split(' ')[0]} on {agent}: {ocr_acs.strip()}, {ocr_kills.strip()}, {ocr_deaths.strip()}, {ocr_assists.strip()}, {ocr_econ.strip()}, {ocr_fb.strip()}, {ocr_p.strip()}, {ocr_d.strip()}")
        #Update player stats, using 0 if not found
        _, current_acs, current_kills, current_deaths, current_assists, current_econ, current_fb, current_p, current_d = players[ocr_name.split(' ')[0]]
        if ocr_acs.strip():
            current_acs = ocr_acs.strip()

        current_kills = current_deaths = current_assists = '-1'
        if ocr_kills.strip():
            current_kills = ocr_kills.strip()
        if ocr_deaths.strip():
            current_deaths = ocr_deaths.strip()
        if ocr_assists.strip():
            current_assists = ocr_assists.strip()
        if ocr_econ.strip():
            current_econ = ocr_econ.strip()
        if ocr_fb.strip():
            current_fb = ocr_fb.strip()
        if ocr_p.strip():
            current_p = ocr_p.strip()
        if ocr_d.strip():
            current_d = ocr_d.strip()
        players[ocr_name.split(' ')[0]] = current_agent, current_acs, current_kills, current_deaths, current_assists, current_econ, current_fb, current_p, current_d


        #Draw rectangles and text on the result image
        cv.rectangle(img_result, (strip_x, strip_y), (strip_x + strip_w, strip_y + strip_h), (255, 0, 0), 2)
        cv.putText(img_result, f"{ocr_name.split(' ')[0]}", (strip_x, strip_y + 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'ACS: {current_acs}', (strip_x + 320, strip_y+ 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Kills: {current_kills}', (strip_x + 420, strip_y+ 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Deaths: {current_deaths}', (strip_x + 500, strip_y+ 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Assists: {current_assists}', (strip_x + 600, strip_y+ 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Econ: {current_econ.strip()}', (strip_x + 700, strip_y+ 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'FB: {current_fb.strip()}', (strip_x + 880, strip_y+ 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Plants: {current_p.strip()}', (strip_x + 980, strip_y+ 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
        cv.putText(img_result, f'Defuses: {current_d.strip()}', (strip_x + 1080, strip_y+ 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)


    #Save result
    output_path = f'scoreboard_result{args.filename}'
    #cv.imshow('Result', img_result)
    #cv.waitKey(0)
    cv.imwrite(output_path, img_result)

    #Ensure valid map name
    for map_name in maps:
        if map_name.lower() in ocr_map.lower():
            ocr_map = map_name
            break

    #Convert players dictionary into a single JSON structure
    players = dict(players)
    result = {
        "map": ocr_map.strip(),
        "w_points": ocr_s0,
        "l_points": ocr_s1,
        "players": [
            {
                "name": name,
                "agent": agent,
                "acs": stats[0] if len(stats) > 0 else "-1",
                "kills": stats[1] if len(stats) > 1 else "-1",
                "deaths": stats[2] if len(stats) > 1 else "-1",
                "assists": stats[3] if len(stats) > 1 else "-1",
                "econ": stats[4] if len(stats) > 2 else "-1",
                "fb": stats[5] if len(stats) > 3 else "-1",
                "plants": stats[6] if len(stats) > 4 else "-1",
                "defuses": stats[7] if len(stats) > 5 else "-1"
            }
            for name, (agent, *stats) in players.items()
        ]
    }

    #Create JSON output directory if doesn't
    json_output_dir = 'JSON'
    os.makedirs(json_output_dir, exist_ok=True)

    #Write JSON to file
    json_output_path = os.path.join(json_output_dir, f'players_{args.filename.replace(".png","")}.json')
    json_output_path = json_output_path.replace(".jpg", "")

    # with open(json_output_path, 'w') as json_file:
    #     json.dump(result, json_file, indent=4)
    sys.stdout.write(json.dumps(result)) #Ensures only the JSON result is sent to stdout
    # return json_file

if __name__ == '__main__':
    main()