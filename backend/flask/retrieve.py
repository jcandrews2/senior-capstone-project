from flask import Blueprint, jsonify, request
import pymysql
from db import get_db_connection

retrieve_bp = Blueprint("retrieve", __name__)

@retrieve_bp.route("/get_players/<gameType>/<gameId>", methods=["GET"])
def get_players(gameType, gameId):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    try:
        if gameType == "val":
            # First get the match info to see which schools are winning and losing
            cursor.execute("""
                SELECT w_school, l_school
                FROM val_picture
                WHERE game_id = %s
            """, (gameId,))
            
            match_info = cursor.fetchone()
            
            if match_info:
                w_school = match_info["w_school"]
                l_school = match_info["l_school"]
                
                # Now get the player data with correct W/L markings
                query = """
                    SELECT 
                        player_name as name, 
                        combat_score, 
                        kills, 
                        deaths, 
                        assists, 
                        econ, 
                        fb, 
                        plants, 
                        defuses, 
                        agent, 
                        school,
                        map,
                        CASE 
                            WHEN school = %s THEN 'W'
                            WHEN school = %s THEN 'L'
                            ELSE school
                        END as school_marker
                    FROM val_game
                    WHERE game_id = %s
                """
                cursor.execute(query, (w_school, l_school, gameId))
                
                # Process results to use the school_marker as school
                players = cursor.fetchall()
                players_list = []
                
                for player in players:
                    player_dict = dict(player)
                    player_dict["original_school"] = player_dict["school"]  # keep original for reference
                    player_dict["school"] = player_dict["school_marker"]    # use marker (W/L) as school
                    del player_dict["school_marker"]                        # remove temp field
                    players_list.append(player_dict)
                
                return jsonify({"players": players_list}), 200
            else:
                # Fall back to original query if match info not found
                query = """
                    SELECT player_name as name, combat_score, kills, deaths, assists, econ, fb, plants, defuses, agent, school, map
                    FROM val_game
                    WHERE game_id = %s
                """
                cursor.execute(query, (gameId,))
        elif gameType == "rl":
            query = """
                SELECT player_name as name, score, goals, assists, saves, shots
                FROM rl_game
                WHERE game_id = %s
            """
        elif gameType == "apex":
            query = """
                SELECT player_name as name, kills, assists, knocks, damage, placement
                FROM apex_game
                WHERE game_id = %s
            """
        else:
            return jsonify({"error": "Invalid game type"}), 400

        cursor.execute(query, (gameId,))
        players = cursor.fetchall()
        players_list = [dict(player) for player in players]
        print(players_list)
        return jsonify({"players": players_list}), 200

    except Exception as e:
        print("Error fetching players info:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()