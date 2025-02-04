import re
from flask import Blueprint, jsonify, request
import pymysql
from db import get_db_connection
import os
import subprocess
import json

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

    # Save the uploaded file
    UPLOAD_FOLDER = 'uploads/'
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Generate a public URL for the image
    file_url = f"{request.host_url}uploads/{file.filename}"

    try:
        if game not in ocr_scripts:
            return jsonify({"error": f"OCR not supported for game: {game}"}), 400

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

# Upload new match data (or update existing)
@upload_bp.route('/upload_match', methods=['POST, PUT'])
def upload_match():
    conn = get_db_connection()
    # cursor = conn.cursor(pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    
    if request.args == "POST": 

        data = request.json  # JSON data from frontend

        # Define game-specific insert queries
        game_queries = {
            "RL": """
                INSERT INTO rl_game (game_id, school, player_name, score, goals, assists, saves, shots, team_score, did_win, opponent, opponent_score, game_number, week_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE score = VALUES(score), goals = VALUES(goals), assists = VALUES(assists), saves = VALUES(saves), shots = VALUES(shots)
            """,
            "Val": """
                INSERT INTO val_game (game_id, school, player_name, combat_score, kills, deaths, assists, econ, fb, plants, defuses, agent, map, team_score, did_win, opponent, opponent_score, game_num, week_num)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE combat_score = VALUES(combat_score), kills = VALUES(kills), deaths = VALUES(deaths), assists = VALUES(assists), econ = VALUES(econ), fb = VALUES(fb), plants = VALUES(plants), defuses = VALUES(defuses), agent = VALUES(agent), map = VALUES(map)
            """,
            "Apex": """
                INSERT INTO apex_game (game_id, school, player_name, kills, assists, knocks, damage, score, placement, game_number, week_number)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE kills = VALUES(kills), assists = VALUES(assists), knocks = VALUES(knocks), damage = VALUES(damage), score = VALUES(score), placement = VALUES(placement)
            """,
        }

        try:
            game = data.get("game")
            if game not in game_queries:
                return jsonify({"error": f"Game '{game}' is not supported"}), 400

            # Insert or update data for each player
            for player in data["players"]:
                if game == "RL":
                    cursor.execute(
                        game_queries[game],
                        (
                            data["game_id"], player["school"], player["playerName"],
                            player["score"], player["goals"], player["assists"],
                            player["saves"], player["shots"],
                            data.get("team_score"), data.get("did_win"),
                            data["opponent"], data.get("opponent_score"),
                            data.get("game_number"), data.get("week")
                        )
                    )
                elif game == "Val":
                    cursor.execute(
                        game_queries[game],
                        (
                            data["game_id"], player["school"], player["playerName"],
                            player["combat_score"], player["kills"], player["deaths"],
                            player["assists"], player["econ"], player["fb"],
                            player["plants"], player["defuses"], player["agent"], player["map"],
                            data.get("team_score"), data.get("did_win"),
                            data["opponent"], data.get("opponent_score"),
                            data.get("game_num"), data.get("week")
                        )
                    )
                elif game == "Apex":
                    cursor.execute(
                        game_queries[game],
                        (
                            data["game_id"], player["school"], player["playerName"],
                            player["kills"], player["assists"], player["knocks"],
                            player["damage"], player["score"], player["placement"],
                            data.get("game_num"), data.get("week")
                        )
                    )

            return jsonify({"message": "Match data uploaded successfully"}), 200
        except Exception as e:
            print(f"Error uploading match data: {e}")
            return jsonify({"error": str(e)}), 500
        finally:
            cursor.close()
            conn.commit()
            conn.close()

    elif request.args == 'PUT': 
        
        # update weekly and seasonal tables here
        
        try: 
            # insert queryies for updating
            
            
            data = request.json
            
            # DATA FORMAT
            # formData.append("file", file);
            # formData.append("game", game);
            # formData.append("week", week);
            # formData.append("school", school);
            # formData.append("opponent_school", opponent_school)
            
            # DO SHIT HERE
            
            return jsonify({"message": "Weekly and season tables updated successfully."}), 200
        
        
        
        except Exception as e:
            print(e)
            return jsonify({"error": str(e)}), 500
        
        finally:
            cursor.close()
            conn.commit()
            conn.close()
            