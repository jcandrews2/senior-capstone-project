from flask import Blueprint, jsonify, request
import pymysql
from urllib.parse import unquote
from db import get_db_connection

player_bp = Blueprint('player', __name__)

@player_bp.route('/player/<videogame>', methods=['GET'])
def get_player_stats(videogame):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    data = request.args.get('player')
    player = unquote(data)

    game_queries = { 
        "rl": "SELECT school, player_name, score, goals, assists, saves, shots from rl_game WHERE player_name = %s",
        "val": "SELECT school, player_name, combat_score, kills, deaths, assists, econ, fb, plants, defuses from val_game WHERE player_name = %s",
        "apex": "SELECT school, player_name, kills, assists, knocks, damage, score from apex_game WHERE player_name = %s",
        }
    
    try:
        cursor.execute(game_queries[videogame], (player,))

        reports = cursor.fetchall()

        if not reports:
            return jsonify({"error": "No stats found for player."}), 404
  
        return jsonify(reports), 200
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()