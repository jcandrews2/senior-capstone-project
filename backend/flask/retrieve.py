from flask import Blueprint, jsonify, request
from db import get_db_connection

retrieve_bp = Blueprint('retrieve', __name__)

@retrieve_bp.route('/get_match_images', methods=['GET'])
def get_match_images():
    """Retrieve uploaded match images based on game, week, and school."""
    
    conn = get_db_connection()
    cursor = conn.cursor()

    game = request.args.get("game")
    week_number = request.args.get("week_number")
    school = request.args.get("school")
    game_number = request.args.get("game_number")

    if not game:
        return jsonify({"error": "Game type is required"}), 400

    picture_tables = {
        "rocket-league": "rl_picture",
        "valorant": "val_picture",
        "apex-legends": "apex_picture"
    }

    if game not in picture_tables:
        return jsonify({"error": f"Game '{game}' is not supported"}), 400

    table_name = picture_tables[game]

    query = f"SELECT game_id, game_number, week_number, school, picture FROM {table_name} WHERE 1=1"
    params = []

    if week_number:
        query += " AND week_number = %s"
        params.append(week_number)
    if school:
        query += " AND school = %s"
        params.append(school)
    if game_number:
        query += " AND game_number = %s"
        params.append(game_number)

    try:
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()

        if not results:
            return jsonify({"message": "No images found for the given filters"}), 404

        image_data = [
            {
                "game_id": row[0],
                "game_number": row[1],
                "week_number": row[2],
                "school": row[3],
                "image_url": row[4],
            } 
            for row in results
        ]

        return jsonify({"images": image_data}), 200

    except Exception as e:
        print(f"Error retrieving match images: {e}")
        return jsonify({"error": "Failed to retrieve match images"}), 500

    finally:
        cursor.close()
        conn.close()