import re
from flask import Blueprint, jsonify, request
import pymysql
from db import get_db_connection
import os
import subprocess
import json
import uuid

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/upload_file', methods=['POST'])
def upload_file():
    ocr_scripts = {
        'valorant': "../ocr/Valorant/ValMatch/ValOCRMain.py",
        'apex-legends': "../ocr/Apex/ApexFuncs.py",
    }
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    school = request.form.get('school')
    opponent_school = request.form.get('opponent_school')
    week = request.form.get('week')
    game = request.form.get('game')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if game not in ocr_scripts:
        return jsonify({"error": f"OCR not supported for game: {game}"}), 400

    # Save the uploaded file
    UPLOAD_FOLDER = 'uploads/'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Generate a **unique** filename to prevent overwriting (UUID + original extension)
    file_extension = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
    file.save(file_path)

    # Generate a **correct** public URL for the uploaded image
    base_url = request.host_url.rstrip('/')  # Ensures no double slashes
    file_url = f"{base_url}/{UPLOAD_FOLDER}{unique_filename}"

    try:
        # Define the OCR script path
        ocr_script = os.path.join(os.path.dirname(__file__), ocr_scripts[game])

        # Run the OCR script and capture JSON output
        process = subprocess.run(
            ["python", ocr_script, "-f", file_path],
            capture_output=True,
            text=True,
            check=True
        )

        # Extract JSON output from stdout
        ocr_output = process.stdout.strip()
        ocr_data = json.loads(ocr_output)
        
        
        # Format the output to include all required attributes
        formatted_data = {
            "image_url": file_url,
            "game": game,  # Assuming the game is Valorant for this OCR
            "week": week,  # Week will need to be added manually in the ModifyPage
            "school": school,  # School will need to be added manually in the ModifyPage
            "opponent_school": opponent_school,  # Opponent will need to be added manually in the ModifyPage
            "map": ocr_data.get("map", ""),
            "code": ocr_data.get("code", ""),
            "squad_placed": ocr_data.get("squad_placed", ""),
            "w_points": ocr_data.get("w_points", ""),
            "l_points": ocr_data.get("l_points", ""),
            "players": ocr_data.get("players", []),
        }

        return jsonify(formatted_data), 200

    except FileNotFoundError:
        return jsonify({"error": "OCR output file not found"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Failed to decode OCR output"}), 500
    except subprocess.CalledProcessError as e:
        print(f"OCR script error: {e.stderr}")
        return jsonify({"error": "OCR processing failed"}), 500

@upload_bp.route('/upload_match', methods=['POST', 'PUT'])
def upload_match():
    conn = get_db_connection()
    cursor = conn.cursor()

    data = request.json  # JSON data from frontend
    game = data.get("game")
    print(data)
    
    if request.method == "POST":
        try:
            if game not in ["rocket-league", "valorant", "apex-legends"]:
                return jsonify({"error": f"Game '{game}' is not supported"}), 400

            # 🔹 Generate a new unique game_id if one isn't provided
            game_id = data.get("game_id", str(uuid.uuid4()))

            # Ensure the image URL is correctly formatted
            image_url = data.get("image_url", "").strip()
            if not image_url.startswith("http"):
                return jsonify({"error": "Invalid image URL"}),

            # Define game-specific queries for the **game tables**
            game_queries = {
                "rocket-league": """
                    INSERT INTO rl_game (game_id, school, player_name, score, goals, assists, saves, shots, did_win, game_number, week_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                "valorant": """
                    INSERT INTO val_game (game_id, school, player_name, combat_score, kills, deaths, assists, econ, fb, plants, defuses, agent, map, did_win, game_number, week_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
                "apex-legends": """
                    INSERT INTO apex_game (game_id, school, player_name, kills, assists, knocks, damage, score, placement, game_number, week_number)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                """,
            }
            
            # Define queries for the **picture tables**
            picture_queries = {
                "rocket-league": """
                    INSERT INTO rl_picture (game_id, game_number, week_number, w_school, l_school, w_points, l_points, picture)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                "valorant": """
                    INSERT INTO val_picture (game_id, game_number, week_number, w_school, l_school, w_points, l_points, picture)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                """,
                "apex-legends": """
                    INSERT INTO apex_picture (game_id, game_number, week_number, school, picture, verified)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """,
            }

            # Insert player data into **game tables**
            for player in data["players"]:
                if game == "rocket-league":
                    cursor.execute(
                        game_queries[game],
                        (
                            game_id, data["school"], player["playerName"],
                            player["score"], player["goals"], player["assists"],
                            player["saves"], player["shots"], 
                            data.get("did_win"), data.get("game_number"), data.get("week")
                        )
                    )
                elif game == "valorant":
                    cursor.execute(
                        game_queries[game],
                        (
                            game_id, data["school"], player["name"],
                            player["acs"], player["kills"], player["deaths"],
                            player["assists"], player["econ"], player["fb"],
                            player["plants"], player["defuses"], player["agent"], data["map"],
                            data.get("did_win"), data.get("game_number"), data.get("week")
                        )   
                    )
                elif game == "apex-legends":
                    cursor.execute(
                        game_queries[game],
                        (
                            game_id, data["school"], player["name"],
                            player["kills"], player["assists"], player["knocks"],
                            player["damage"], player["score"], player["placement"],
                            data.get("game_number"), data.get("week")
                        )   
                    )
            
            # Insert data into the **picture tables**
            if game == "rocket-league":
                cursor.execute(
                    picture_queries[game],
                    (
                        game_id, data.get("game_number"), data.get("week"), data["school"],
                        data["opponent_school"], data["w_points"], data["l_points"], data["image_url"]
                    )
                )
            elif game == "valorant":
                cursor.execute(
                    picture_queries[game],
                    (
                        game_id, data.get("game_number"), data.get("week"), data["school"],
                        data["opponent_school"], data["w_points"], data["l_points"], data["image_url"]
                    )
                )
            elif game == "apex-legends":
                cursor.execute(
                    picture_queries[game],
                    (
                        game_id, data.get("game_number"), data.get("week"), data["school"],
                        data["image_url"], True  # Verified = True by default
                    )
                )

            conn.commit()
            return jsonify({"message": "Match data uploaded successfully", "game_id": game_id}), 200
        
        except Exception as e:
            conn.rollback()
            print(f"Error uploading match data: {e}")
            return jsonify({"error": str(e)}), 500
        
        finally:
            cursor.close()
            conn.close()