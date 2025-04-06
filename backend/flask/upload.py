from flask import Blueprint, jsonify, request, send_from_directory
import pymysql
from db import get_db_connection
import os
import subprocess
import uuid
import json
import uuid
import math
import copy

upload_bp = Blueprint('upload', __name__)

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")

@upload_bp.route('/get_upload/<game_id>', methods=['GET'])
def get_upload(game_id): 

    try:
        file_name = game_id + ".png"
        print(file_name)
        file_path = os.path.join(UPLOAD_FOLDER, file_name)
        print(file_path)
        if not os.path.exists(file_path):
            return jsonify({"error": "File not found on server"}), 404
        
        return send_from_directory(UPLOAD_FOLDER, file_name)
        
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500


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
    game_number = request.form.get('game_number')

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    if game not in ocr_scripts:
        return jsonify({"error": f"OCR not supported for game: {game}"}), 400

    # Save the uploaded file
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Generate a **unique** filename to prevent overwriting (UUID + original extension)
    file_extension = os.path.splitext(file.filename)[1]
    game_id = uuid.uuid4()
    unique_filename = f"{game_id}{file_extension}"
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
            "game_id": game_id,
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
            "game_number": game_number
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
    
    # Check if this is a reupload from a dispute
    is_dispute_edit = data.get("disputes") and len(data.get("disputes", [])) > 0
    print(f"Processing {'dispute edit' if is_dispute_edit else 'new upload'}")
    
    if request.method == "POST":
        try:
            if game not in ["rocket-league", "valorant", "apex-legends"]:
                return jsonify({"error": f"Game '{game}' is not supported"}), 400

            # Use existing game_id (for disputes) or generate a new one
            game_id = data.get("game_id")
            
            # For new uploads, generate UUID if not provided
            if not game_id or game_id == "-1":
                game_id = str(uuid.uuid4())
                print(f"Generated new game_id: {game_id}")
            else:
                print(f"Using existing game_id: {game_id}")
                
                # For dispute edits, we need to clean up existing entries before reinserting
                if is_dispute_edit:
                    game_type_tables = {
                        "rocket-league": "rl_game", 
                        "valorant": "val_game",
                        "apex-legends": "apex_game"
                    }
                    
                    # Delete existing game data to avoid duplicates
                    try:
                        cursor.execute(f"DELETE FROM {game_type_tables[game]} WHERE game_id = %s", (game_id,))
                        print(f"Deleted existing game data for game_id: {game_id}")
                    except Exception as e:
                        print(f"Error deleting existing game data: {e}")

            # Ensure the image URL is correctly formatted
            image_url = data.get("image_url", "").strip()
            if not image_url.startswith("http") and not image_url.startswith("/"):
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
                    INSERT INTO apex_picture (game_id, game_number, week_number, school, picture)
                    VALUES (%s, %s, %s, %s, %s);
                """, 
            }
            
            # Define picture tables for deletion on dispute edits
            picture_tables = {
                "rocket-league": "rl_picture",
                "valorant": "val_picture",
                "apex-legends": "apex_picture"
            }
            
            # For dispute edits, delete existing picture data too
            if is_dispute_edit:
                try:
                    cursor.execute(f"DELETE FROM {picture_tables[game]} WHERE game_id = %s", (game_id,))
                    print(f"Deleted existing picture data for game_id: {game_id}")
                except Exception as e:
                    print(f"Error deleting existing picture data: {e}")
            
            # insert queries for picture tables
            if game == "rocket-league":
                cursor.execute(
                    picture_queries[game],
                    (
                        game_id, data.get("game_number"), data.get("week"), data["school"],
                        data["opponent_school"], data.get("w_points", ""), data.get("l_points", ""), data["image_url"]
                    )
                )
            elif game == "valorant":
                cursor.execute(
                    picture_queries[game],
                    (
                        game_id, data.get("game_number", "-1"), data.get("week"), data["school"],
                        data["opponent_school"], data.get("w_points", ""), data.get("l_points", ""), data["image_url"]
                    )
                )
            elif game == "apex-legends":
                cursor.execute(
                    picture_queries[game],
                    (
                        game_id, data.get("game_number"), data.get("week"), data["school"],
                        data["image_url"]
                    )
                )

            # Insert player data for apex and RL
            print(data)
            for player in data["players"]:
                if game == "apex-legends":
                    #insert score per game
                    points = 0
                    damage = 0
                    for ply in data["players"]:
                        damage += int(ply["damage"])
                        points += int(ply["kills"])
                        
                    points += math.floor(damage/200)
                    
                    placement = int(data.get("squad_placed"))
                    if placement == 1:
                        points += 12
                    elif placement == 2:
                        points += 9
                    elif placement == 3:
                        points += 7
                    elif placement == 4:
                        points += 5
                    elif placement == 5:
                        points += 4
                    elif placement == 6 or 7:
                        points += 3
                    elif placement == 8 or 9 or 10:
                        points += 2
                    elif placement == 11 or 12 or 13 or 14 or 15:
                        points += 1
                    cursor.execute(
                        game_queries[game],
                            (
                            game_id, data["school"], player["name"],
                            player["kills"], player["assists"], player["knocks"],
                            player["damage"], points, data.get("squad_placed"),
                            data.get("game_number"), data.get("week")
                            )  
                        )
                    
                    #check to see if this player exists in the table
                    cursor.execute(f"""SELECT COUNT(*) from apex_week where player_name="{player["name"]}" and week_number ={data["week"]};""")
                    is_week_exists = cursor.fetchone()
                    
                    #if 0, it doesnt exist, so insert
                    if is_week_exists[0] == 0:
                        cursor.execute(f"""INSERT INTO apex_week(week_number, school, player_name, week_kills_avg, week_assists_avg, week_knocks_avg, week_damage_avg, week_kills, week_assists, week_knocks, week_damage, week_score, week_placements_1, week_placements_2, week_placements_3, week_placements_4, week_placements_5, week_placements_6_7, week_placements_8_10, week_placements_11_15)
                            SELECT week_number, school, player_name, AVG(kills), AVG(assists), AVG(knocks), AVG(damage), SUM(kills), SUM(assists), SUM(knocks), SUM(damage), SUM(score), 0, 0, 0, 0, 0, 0, 0, 0
                            FROM apex_game
                            WHERE player_name='{player["name"]}' and week_number={data["week"]}
                            GROUP BY week_number, school, player_name;
                            """)
                    
                    #if 1, does exists and needs to be updated        
                    if is_week_exists[0] == 1:
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_kills_avg = (
                        SELECT AVG(kills)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}'  AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ;
                        """)
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_assists_avg = (
                        SELECT AVG(assists)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}'  AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ;
                        """)
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_knocks_avg = (
                        SELECT AVG(knocks)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}' AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ;
                        """)
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_damage_avg = (
                        SELECT AVG(damage)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}'  AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ;
                        """)
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_kills = (
                        SELECT SUM(kills)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}'  AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ;
                        """)
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_assists = (
                        SELECT SUM(assists)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}'  AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ;
                        """)
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_knocks = (
                        SELECT SUM(knocks)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}'  AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ;
                        """)
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_damage = (
                        SELECT SUM(damage)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}'  AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ; 
                        """)
                        cursor.execute(f"""UPDATE apex_week
                        SET apex_week.week_score = (
                        SELECT SUM(score)
                        FROM apex_game
                        WHERE apex_game.player_name = '{player["name"]}'  AND apex_game.week_number = {data["week"]}
                        )
                        WHERE apex_week.player_name = '{player["name"]}' AND apex_week.week_number = {data["week"]} ; 
                        """)
                    
                    #update placements for week
                    print(placement)
                    if placement == 1:
                        cursor.execute(f"""UPDATE apex_week 
                            SET week_placements_1 = week_placements_1 + 1
                            WHERE player_name = '{player["name"]}' AND week_number = {data["week"]} ;
                            """)
                    elif placement == 2:
                        cursor.execute(f"""UPDATE apex_week 
                            SET week_placements_2 = week_placements_2 + 1
                            WHERE player_name = '{player["name"]}' AND week_number = {data["week"]} ;
                            """)
                    elif placement == 3:
                        cursor.execute(f"""UPDATE apex_week 
                            SET week_placements_3 = week_placements_3 + 1
                            WHERE player_name = '{player["name"]}' AND week_number = {data["week"]} ;
                            """)
                    elif placement == 4:
                        cursor.execute(f"""UPDATE apex_week 
                            SET week_placements_4 = week_placements_4 + 1
                            WHERE player_name = '{player["name"]}' AND week_number = {data["week"]} ;
                            """)
                    elif placement == 5:
                        cursor.execute(f"""UPDATE apex_week 
                            SET week_placements_5 = week_placements_5 + 1
                            WHERE player_name = '{player["name"]}' AND week_number = {data["week"]} ;
                            """)
                    elif placement == 6 or 7:
                        cursor.execute(f"""UPDATE apex_week 
                            SET week_placements_6_7 = week_placements_6_7 + 1
                            WHERE player_name = '{player["name"]}' AND week_number = {data["week"]} ;
                            """)
                    elif placement == 8 or 9 or 10:
                        cursor.execute(f"""UPDATE apex_week 
                            SET week_placements_8_10 = week_placements_8_10 + 1
                            WHERE player_name = '{player["name"]}' AND week_number = {data["week"]} ;
                            """)
                    elif placement == 11 or 12 or 13 or 14 or 15:
                        cursor.execute(f"""UPDATE apex_week 
                            SET week_placements_11_15 = week_placements_11_15 + 1
                            WHERE player_name = '{player["name"]}' AND week_number = {data["week"]} ;
                            """)
                
             
                
                    #check to see if in season table
                    cursor.execute(f"""SELECT COUNT(*) from apex_season where player_name="{player["name"]}";""")
                    is_season_exists = cursor.fetchone()

                    #if doesnt exist
                    if is_season_exists[0] == 0:
                        cursor.execute(f"""INSERT INTO apex_season(school, player_name, season_kills_avg, season_assists_avg, season_knocks_avg, season_damage_avg, total_kills, total_assists, total_knocks, total_damage, total_score, total_placements_1, total_placements_2, total_placements_3, total_placements_4, total_placements_5, total_placements_6_7, total_placements_8_10, total_placements_11_15)
                            SELECT school, player_name, AVG(week_kills_avg), AVG(week_assists_avg), AVG(week_knocks_avg), AVG(week_damage_avg), SUM(week_kills), SUM(week_assists), SUM(week_knocks), SUM(week_damage), SUM(week_score), SUM(week_placements_1), SUM(week_placements_2), SUM(week_placements_3), SUM(week_placements_4), SUM(week_placements_5), SUM(week_placements_6_7), SUM(week_placements_8_10),   SUM(week_placements_11_15)
                            FROM apex_week
                            WHERE player_name='{player["name"]}';
                            """)
                    #if it does exist then update
                    if is_season_exists[0] == 1:
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.season_kills_avg = (
                        SELECT AVG(week_kills_avg)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' ; 
                        """)
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.season_knocks_avg = (
                        SELECT AVG(week_knocks_avg)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' ; 
                        """)
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.season_damage_avg = (
                        SELECT AVG(week_damage_avg)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' ; 
                        """)
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.season_assists_avg = (
                        SELECT AVG(week_assists_avg)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' 
                        """)
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.total_assists = (
                        SELECT SUM(week_assists)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""
                        UPDATE apex_season
                        SET apex_season.total_knocks = (
                        SELECT SUM(week_knocks)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.total_damage = (
                        SELECT SUM(week_damage)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""
                        UPDATE apex_season
                        SET apex_season.total_score = (
                        SELECT SUM(week_score)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.total_kills = (
                        SELECT SUM(week_kills)
                        FROM apex_week
                        WHERE apex_week.player_name = '{player["name"]}'
                        )
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        
                        #update season placements
                        cursor.execute(f"""UPDATE apex_season 
                        SET apex_season.total_placements_1 = ( 
                        SELECT SUM(week_placements_1) FROM apex_week 
                        WHERE apex_week.player_name = '{player["name"]}' ) 
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.total_placements_2 = ( 
                        SELECT SUM(week_placements_2) 
                        FROM apex_week 
                        WHERE apex_week.player_name = '{player["name"]}' ) 
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season 
                        SET apex_season.total_placements_3 = ( 
                        SELECT SUM(week_placements_3) 
                        FROM apex_week 
                        WHERE apex_week.player_name = '{player["name"]}' ) 
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season 
                        SET apex_season.total_placements_4 = ( 
                        SELECT SUM(week_placements_4) FROM apex_week 
                        WHERE apex_week.player_name = '{player["name"]}' ) 
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season 
                        SET apex_season.total_placements_5 = ( 
                        SELECT SUM(week_placements_5) 
                        FROM apex_week 
                        WHERE apex_week.player_name = '{player["name"]}' ) 
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season 
                        SET apex_season.total_placements_6_7 = ( 
                        SELECT SUM(week_placements_6_7) 
                        FROM apex_week 
                        WHERE apex_week.player_name = '{player["name"]}' ) 
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season
                        SET apex_season.total_placements_8_10 = ( 
                        SELECT SUM(week_placements_8_10) F
                        FROM apex_week 
                        WHERE apex_week.player_name = '{player["name"]}' ) 
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        cursor.execute(f"""UPDATE apex_season 
                        SET apex_season.total_placements_11_15 = ( 
                        SELECT SUM(week_placements_11_15) 
                        FROM apex_week 
                        WHERE apex_week.player_name = '{player["name"]}' ) 
                        WHERE apex_season.player_name = '{player["name"]}' ;
                        """)
                        

                    
                elif game == "rocket-league":
                    cursor.execute(
                        game_queries[game],
                        (
                            game_id, data["school"], player["name"],
                            player["score"], player["goals"], player["assists"],
                            player["saves"], player["shots"], 
                            data.get("did_win"), data.get("game_number"), data.get("week")
                        )
                    )
                    
                            
            #insert player game rows for valorant       
            if game == "valorant":
                
                school = ""
                o_school =""
                did_win = 0
                for player in data["players"]:
                    if player["school"] == "W":
                        school = data["school"]
                        o_school = data["opponent_school"]
                        did_win = 1
                    else:
                        school = data["opponent_school"] 
                        o_school = data["school"]
                        did_win = 0
                    
                    # Validate required fields for Valorant player data
                    try:
                        # Make sure all required fields are present and preserve zero values
                        combat_score = player.get("combat_score", "-1")
                        combat_score = "-1" if combat_score == "" else combat_score  # Only convert empty strings to "-1", keep "0" as "0"
                        
                        kills = player.get("kills", "-1")
                        kills = "-1" if kills == "" else kills
                        
                        deaths = player.get("deaths", "-1")
                        deaths = "-1" if deaths == "" else deaths
                        
                        assists = player.get("assists", "-1")
                        assists = "-1" if assists == "" else assists
                        
                        econ = player.get("econ", "-1")
                        econ = "-1" if econ == "" else econ
                        
                        fb = player.get("fb", "-1")
                        fb = "-1" if fb == "" else fb
                        
                        plants = player.get("plants", "-1")
                        plants = "-1" if plants == "" else plants
                        
                        defuses = player.get("defuses", "-1")
                        defuses = "-1" if defuses == "" else defuses
                        
                        agent = player.get("agent", "Unknown")
                        agent = "Unknown" if agent == "" else agent
                        
                        cursor.execute(
                            game_queries[game],
                            (
                                game_id, school, player["name"],
                                combat_score, kills, deaths,
                                assists, econ, fb,
                                plants, defuses, agent, data["map"],
                                did_win, data["game_number"], data.get("week", "1")
                            )   
                        )
                    except KeyError as e:
                        raise Exception(f"Missing required field: {str(e)}")
                    except Exception as e:
                        raise Exception(f"Error processing player data: {str(e)}")
                
    

                    #Query to see if it exists. Will return a zero or one
                    cursor.execute(f"""SELECT COUNT(*) from val_week where player_name="{player["name"]}" and week_number ={data["week"]};""")
                    
                    #returns if it is zero or one in a tuple format. only need the first item
                    is_week_exists = cursor.fetchone()
                    #if zero insert


                    if is_week_exists[0] == 0 and game == "valorant":
                        cursor.execute(f"""INSERT INTO val_week(week_number, school, player_name, week_cs_avg, week_kills_avg,
                                    week_deaths_avg, week_assists_avg, week_econ_avg, week_fb_avg, week_plants_avg, week_defuses_avg, team_score)
                            SELECT week_number, school, player_name, AVG(combat_score), AVG(kills),
                            AVG(deaths), AVG(assists), AVG(econ), AVG(fb), AVG(plants), AVG(defuses), sum(did_win)
                            FROM val_game
                            WHERE player_name='{player["name"]}' and week_number={data["week"]}
                            GROUP BY week_number, school, player_name;
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.did_win = IF((val_week.team_score) < 2, FALSE, TRUE)
                            WHERE val_week.player_name = '{player["name"]}' and val_week.week_number ={data["week"]};
                            """)
                            
                        # For dispute edits, explicitly set did_win based on school marker
                        if is_dispute_edit and player["school"] == "W":
                            cursor.execute(f"""UPDATE val_week
                                SET val_week.did_win = TRUE
                                WHERE val_week.player_name = '{player["name"]}'
                                AND val_week.week_number = {data["week"]};
                                """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.opponent = '{o_school}'
                            WHERE val_week.player_name = '{player["name"]}' and val_week.week_number ={data["week"]};
                            """)

                    #if returns a one, means its already in the week table so update.
                    if is_week_exists[0] == 1 and game == "valorant":
                        cursor.execute(f"""UPDATE val_week 
                            SET val_week.team_score = ( 
                            SELECT sum(did_win) FROM val_game WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} ) 
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]};
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.week_cs_avg = (
                            SELECT AVG(combat_score) FROM val_game
                            WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} ) 
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]} ;
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.week_kills_avg = (
                            SELECT AVG(kills) 
                            FROM val_game 
                            WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} )
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]};
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.week_deaths_avg = (
                            SELECT AVG(deaths) FROM val_game
                            WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} ) 
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]} ;
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.week_assists_avg = (
                            SELECT AVG(assists)
                            FROM val_game
                            WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} )
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]} ;
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.week_econ_avg = (
                            SELECT AVG(econ) FROM val_game
                            WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} )
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]} ; 
                            """)
                        cursor.execute(f"""UPDATE val_week 
                            SET val_week.week_fb_avg = (
                            SELECT AVG(fb) FROM val_game 
                            WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} )
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]} ;
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.week_plants_avg = (
                            SELECT AVG(plants)
                            FROM val_game 
                            WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} ) 
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]} ;
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.week_defuses_avg = ( 
                            SELECT AVG(defuses)
                            FROM val_game
                            WHERE val_game.player_name = '{player["name"]}' AND val_game.week_number = {data["week"]} )
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]} ;
                            """)
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.did_win = IF((val_week.team_score) < 2, FALSE, TRUE)
                            WHERE val_week.player_name = '{player["name"]}' and val_week.week_number ={data["week"]};
                            """)
                            
                        # For dispute edits, explicitly set did_win based on school marker
                        if is_dispute_edit and player["school"] == "W":
                            cursor.execute(f"""UPDATE val_week
                                SET val_week.did_win = TRUE
                                WHERE val_week.player_name = '{player["name"]}'
                                AND val_week.week_number = {data["week"]};
                                """)
                    
                    #check to see if this player is in the season table    
                    cursor.execute(f"""SELECT COUNT(*) from val_season where player_name="{player["name"]}";""")
                    is_season_exists = cursor.fetchone()
                    print(is_season_exists)
                    
                    #will return a 0 or 1 based on if its the game.
                    #if not in the season table then insert
                    if is_season_exists[0] == 0 and game == "valorant":
                        cursor.execute(f"""INSERT INTO val_season(school, player_name, season_cs_avg, season_kills_avg, season_deaths_avg, season_assists_avg, season_econ_avg, season_fb_avg, season_plants_avg, season_defuses_avg, team_wins)
                            SELECT  school, player_name, AVG(week_cs_avg), AVG(week_kills_avg), AVG(week_deaths_avg), AVG(week_assists_avg), AVG(week_econ_avg), AVG(week_fb_avg), AVG(week_plants_avg), AVG(week_defuses_avg), sum(did_win)
                            FROM val_week
                            WHERE player_name='{player["name"]}' 
                            GROUP BY player_name;
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.team_losses =(
                            SELECT COUNT(*)
                            FROM val_week
                            WHERE val_week.did_win = 0 and val_week.player_name = '{player["name"]}'
                            )
                            WHERE val_season.player_name = '{player["name"]}';
                            """)
                    
                    #if already in the season table then update
                    if is_season_exists[0] == 1 and game == "valorant":
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.season_cs_avg = (
                            SELECT AVG(week_cs_avg)
                            FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.team_wins = (
                            SELECT sum(did_win)
                            FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.team_losses =(
                            SELECT COUNT(*) 
                            FROM val_week
                            WHERE val_week.did_win = 0 and val_week.player_name = '{player["name"]}')
                            WHERE val_season.player_name = '{player["name"]}';
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.season_kills_avg = (
                            SELECT AVG(week_kills_avg)
                            FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.season_deaths_avg = (
                            SELECT AVG(week_deaths_avg)
                            FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.season_assists_avg = (
                            SELECT AVG(week_assists_avg)
                            FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.season_econ_avg = (
                            SELECT AVG(week_econ_avg)
                            FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.season_fb_avg = (
                            SELECT AVG(week_fb_avg) FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.season_plants_avg = (
                            SELECT AVG(week_plants_avg)
                            FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        cursor.execute(f"""UPDATE val_season
                            SET val_season.season_defuses_avg = (
                            SELECT AVG(week_defuses_avg)
                            FROM val_week
                            WHERE val_week.player_name = '{player["name"]}' )
                            WHERE val_season.player_name = '{player["name"]}'
                            """)
                        


                        
                #updates the opponent score for the week. Needs to be done at the end so the rest of the data can be populated    
                for player in data["players"]:
                    if player["school"] == "W":
                        o_school = data["opponent_school"]
                    else:
                        o_school = data["school"]
                    if game == "valorant":
                        cursor.execute(f"""UPDATE val_week
                            SET val_week.opponent_score = (
                            SELECT sum(did_win)/5
                            FROM val_game
                            WHERE val_game.week_number = {data["week"]} and val_game.school = '{o_school}'
                            )
                            WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]}; 
                            """)
                    #if one update
                    
                    #runs picture query for the appropriate game
           
            

            # If this was a dispute edit, let's resolve the dispute in the database
            if is_dispute_edit:
                try:
                    cursor.execute("DELETE FROM disputes WHERE game_id = %s", (game_id,))
                    print(f"Automatically resolved dispute for game_id: {game_id}")
                except Exception as e:
                    print(f"Error resolving dispute: {e}")
            
            conn.commit()  # Save changes

            return jsonify({
                "message": f"Match data {'updated' if is_dispute_edit else 'uploaded'} successfully", 
                "game_id": game_id,
                "dispute_resolved": is_dispute_edit
            }), 200
        
        except Exception as e:
            conn.rollback()
            print(f"Error uploading match data: {e}")
            return jsonify({"error": str(e)}), 500
        
        finally:
            cursor.close()
            conn.close()