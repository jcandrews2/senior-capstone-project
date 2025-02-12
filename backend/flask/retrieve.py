from flask import Blueprint, jsonify, request
import pymysql
from db import get_db_connection

retrieve_bp = Blueprint("retrieve", __name__)

@retrieve_bp.route("/get_players/<gameType>/<gameId>", methods=["GET"])
def get_players(gameType, gameId):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    print("I am in the function")
    try:
        if gameType == "val":
            # query = """
            #     SELECT player_name as name, combat_score, kills, deaths, assists, econ, fb, plants, defuses, agent
            #     FROM val_game
            #     WHERE game_id = %s
            # """
            query = """
            SELECT * FROM val_game WHERE game_id = %s
            """
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
        print("printing players:")
        print(players)
        players_list = [dict(player) for player in players]
        print(players_list)
        return jsonify({"players": players_list}), 200

    except Exception as e:
        print("Error fetching players info:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()