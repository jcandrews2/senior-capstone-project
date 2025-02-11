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
        # Fetch all disputes from the disputes table
        cursor.execute("SELECT * FROM disputes")
        disputes = cursor.fetchall()

        games = {}

        for dispute in disputes:
            game_id = dispute["game_id"]
            videogame = dispute["videogame"]
            picture_table = ""

            # Determine the correct picture table based on game type
            if videogame == "val":
                picture_table = "val_picture"
                query = f"""
                SELECT game_id, game_number, week_number, w_school AS school, l_school AS opponent, w_points, l_points, picture 
                FROM {picture_table} 
                WHERE game_id = %s
                """
            elif videogame == "rl":
                picture_table = "rl_picture"
                query = f"""
                SELECT game_id, game_number, week_number, w_school AS school, l_school AS opponent, w_points, l_points, picture 
                FROM {picture_table} 
                WHERE game_id = %s
                """
            elif videogame == "apex":
                picture_table = "apex_picture"
                query = f"""
                SELECT game_id, game_number, week_number, school, picture 
                FROM {picture_table} 
                WHERE game_id = %s
                """
            else:
                continue  # Skip invalid games

            # Fetch game details from the appropriate `game_picture` table
            cursor.execute(query, (game_id,))
            game_data = cursor.fetchone()

            if not game_data:
                continue  # Skip disputes with no corresponding game

            # If this game_id hasn't been added yet, initialize it
            if game_id not in games:
                games[game_id] = {
                    "gameId": game_id,
                    "gameType": videogame,
                    "school": game_data.get("school"),
                    "opponent": game_data.get("opponent", ""),  # Apex does not have `opponent`
                    "week": f"Week {game_data['week_number']}",
                    "game_number": game_data["game_number"],
                    "w_points": game_data.get("w_points", ""),
                    "l_points": game_data.get("l_points", ""),
                    "image_url": game_data.get("picture"),  # Stores the match screenshot
                    "disputes": [],
                }

            # Append dispute comments under the correct game entry
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

@disputes_bp.route("/resolve_dispute/<gameId>", methods=["POST"])
def resolve_dispute(gameId):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM disputes WHERE game_id = %s", (gameId,))
        conn.commit()
        return jsonify({"message": "Dispute resolved successfully"}), 200
    except Exception as e:
        print(f"Error resolving dispute: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()