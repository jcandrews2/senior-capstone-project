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


# Fetch all disputes grouped by game
@disputes_bp.route("/get_all_disputes", methods=["GET"])
def get_all_disputes():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)  # Ensure dictionary cursor

    try:
        query = """
        SELECT 
            d.game_id, d.username, d.school AS submitter_school, d.comment, d.videogame, d.week_number, d.game_number,
            g.map, g.code, g.school AS game_school, g.opponent
        FROM disputes d
        JOIN games g ON d.game_id = g.game_id
        """
        cursor.execute(query)
        disputes = cursor.fetchall()

        # Group disputes by game
        games = {}
        for row in disputes:
            game_id = row["game_id"]
            if game_id not in games:
                games[game_id] = {
                    "gameId": game_id,
                    "gameType": row["videogame"],
                    "map": row["map"],
                    "code": row["code"],
                    "school": row["game_school"],
                    "opponent": row["opponent"],
                    "week": f"Week {row['week_number']}",
                    "game_number": row["game_number"],
                    "disputes": [],
                }
            games[game_id]["disputes"].append(
                {
                    "username": row["username"],
                    "school": row["submitter_school"],
                    "comment": row["comment"],
                }
            )

        return jsonify(list(games.values())), 200

    except Exception as e:
        print(f"Error fetching disputes: {e}")
        return jsonify({"error": "Failed to fetch disputes"}), 500

    finally:
        cursor.close()
        conn.close()


# Resolve a dispute (delete by game_id)
@disputes_bp.route("/resolve_dispute/<int:game_id>", methods=["POST"])
def resolve_dispute(game_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Remove disputes for the given game ID
        cursor.execute("DELETE FROM disputes WHERE game_id = %s", (game_id,))
        conn.commit()

        return jsonify({"message": "Dispute resolved successfully"}), 200

    except Exception as e:
        print(f"Error resolving dispute: {e}")
        return jsonify({"error": "Failed to resolve dispute"}), 500

    finally:
        cursor.close()
        conn.close()