from flask import Blueprint, jsonify, request
import pymysql
from db import get_db_connection
import os
import subprocess
from urllib.parse import unquote
import uuid
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
    game_number = request.form.get('game_number')

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
                    INSERT INTO apex_picture (game_id, game_number, week_number, school, picture)
                    VALUES (%s, %s, %s, %s, %s);
                """, 
            }
            
            # insert queries for picture tables
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
                            game_id, data.get("game_number", "-1"), data.get("week"), data["school"],
                            data["opponent_school"], data["w_points"], data["l_points"], data["image_url"]
                        )
                    )
            elif game == "apex-legends":
                cursor.execute(
                        picture_queries[game],
                        game_id, data.get("game_number"), data.get("week"), data["school"],
                        data["image_url"]
                    )
                
            # Insert player data
            print(data)
            
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
                    
                if game == "rocket-league":
                    cursor.execute(
                        game_queries[game],
                        (
                            game_id, school, player["name"],
                            player["score"], player["goals"], player["assists"],
                            player["saves"], player["shots"], 
                            data.get("did_win"), data.get("game_number"), data.get("week")
                        )
                    )
                elif game == "valorant":
                    cursor.execute(
                        game_queries[game],
                        (
                            game_id, school, player["name"],
                            player["acs"], player["kills"], player["deaths"],
                            player["assists"], player["econ"], player["fb"],
                            player["plants"], player["defuses"], player["agent"], data["map"],
                            did_win, data["game_number"], data.get("week", "1")
                        )   
                    )
                elif game == "apex-legends":
                    cursor.execute(
                        game_queries[game],
                        (
                            game_id, school, player["name"],
                            player["kills"], player["assists"], player["knocks"],
                            player["damage"], player["score"], player["placement"],
                            data.get("game_number"), data.get("week")
                        )   
                    )
            
  

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
                        GROUP by map
                        )
                        WHERE val_week.player_name = '{player["name"]}' AND val_week.week_number = {data["week"]}; 
                        """)
                #if one update
                
                #runs picture query for the appropriate game
           
            

            conn.commit()  # Save changes

            return jsonify({"message": "Match data uploaded successfully", "game_id": game_id}), 200
        
        except Exception as e:
            conn.rollback()
            print(f"Error uploading match data: {e}")
            return jsonify({"error": str(e)}), 500
        
        finally:
            cursor.close()
            conn.close()