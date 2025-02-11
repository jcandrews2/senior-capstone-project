from flask import Blueprint, jsonify, request
from db import get_db_connection
import pymysql

rankings_bp = Blueprint('rankings', __name__)

@rankings_bp.route('/get_rankings/<videogame>', methods=['GET'])
def get_rankings(videogame):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:

        rankings_queries = { 
            "rl": 'SELECT school, season_wins_total AS `wins`, season_losses_total AS `losses` FROM rl_season GROUP BY school ORDER BY season_wins_total DESC',
            "val": 'SELECT school, team_wins AS `wins`, team_losses AS `losses` FROM val_season GROUP BY school ORDER BY team_wins DESC',
            "apex": 'SELECT school, total_score AS `score` FROM apex_season GROUP BY school ORDER BY total_score DESC',
        }

        cursor.execute(rankings_queries[videogame])

        rankings = cursor.fetchall()

        return jsonify(rankings), 200


    except Exception as e: 
        print(e)
        return jsonify({"error": str(e)}), 500

    finally: 
        cursor.close()
        conn.close()