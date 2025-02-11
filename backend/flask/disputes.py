from flask import Blueprint, jsonify, request
import pymysql
from db import get_db_connection

disputes_bp = Blueprint("disputes", __name__)

# Submit a dispute
@disputes_bp.route("/submit_dispute/<videogame>", methods=["POST"])
def submit_dispute(videogame):
    conn = get_db_connection()
    cursor = conn.cursor()

    data = request.get_json()
    game_id = data.get('game_id')
    username = data.get('username')
    school = data.get('school')
    comment = data.get('comment')
    week_number = data.get('week_number')
    game_number = data.get('game_number')

    try:
        cursor.execute("INSERT INTO disputes (game_id, username, school, comment, videogame, week_number, game_number) VALUES (%s, %s, %s, %s, %s, %s, %s)", (game_id, username, school, comment, videogame, week_number, game_number))
        
        return jsonify({"message": "Dispute submitted successfully"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

    finally:
        conn.commit()
        cursor.close()
        conn.close()


@disputes_bp.route("/get_all_disputes", methods=["GET"])
def get_all_disputes():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Ensure dictionary cursor

    try:
        # First, fetch all disputes
        cursor.execute("SELECT * FROM disputes")
        disputes = cursor.fetchall()

        games = {}

        for dispute in disputes:
            game_id = dispute["game_id"]
            videogame = dispute["videogame"]
            game_table = ""

            # Determine the game table dynamically
            if videogame == "valorant":
                game_table = "val_game"
            elif videogame == "rocket-league":
                game_table = "rl_game"
            elif videogame == "apex-legends":
                game_table = "apex_game"
            else:
                continue  # Skip invalid games

            # Fetch game details from the appropriate table
            query = f"""
            SELECT game_id, map, code, school AS game_school, opponent 
            FROM {game_table} 
            WHERE game_id = %s
            """
            cursor.execute(query, (game_id,))
            game_data = cursor.fetchone()

            if not game_data:
                continue  # Skip disputes with no corresponding game

            if game_id not in games:
                games[game_id] = {
                    "gameId": game_id,
                    "gameType": videogame,
                    "map": game_data.get("map"),
                    "code": game_data.get("code"),
                    "school": game_data.get("game_school"),
                    "opponent": game_data.get("opponent"),
                    "week": f"Week {dispute['week_number']}",
                    "game_number": dispute["game_number"],
                    "disputes": [],
                }

            games[game_id]["disputes"].append(
                {
                    "username": dispute["username"],
                    "school": dispute["school"],
                    "comment": dispute["comment"],
                }
            )

        return jsonify(list(games.values())), 200

    except Exception as e:
        print(f"Error fetching disputes: {e}")
        return jsonify({"error": "Failed to fetch disputes"}), 500

    finally:
        cursor.close()
        conn.close()