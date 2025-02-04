from flask import Blueprint, jsonify, request
import pymysql
from urllib.parse import unquote
from db import get_db_connection

roster_bp = Blueprint('roster', __name__)

@roster_bp.route('/roster/<videogame>', methods=['GET', 'PUT', 'POST', 'DELETE'])
def roster(videogame):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == "GET":
        data = request.args.get('school')
        school = unquote(data)
        try: 

            get_roster_queries = { 
                "rl": "SELECT player_name from rl_roster WHERE school = %s",
                "val": "SELECT player_name from val_roster WHERE school = %s",
                "apex": "SELECT player_name from apex_roster WHERE school = %s"
            }

            cursor.execute(get_roster_queries[videogame], (school,))

            roster = [slot['player_name'] for slot in cursor.fetchall()]

            return jsonify(roster), 200

        except Exception as e: 
            print(e)
            return jsonify({"error": str(e)}), 500
        
        finally: 
            cursor.close()
            conn.close()

    elif request.method == "POST": 
        try: 
            data = request.get_json()
            school = data.get('school')
            roster = data.get('roster')

            post_roster_queries = { 
                "rl": "INSERT INTO rl_roster (school, player_name) VALUES (%s, %s)",
                "val": "INSERT INTO val_roster (school, player_name) VALUES (%s, %s)",
                "apex": "INSERT INTO apex_roster (school, player_name) VALUES (%s, %s)"
            }

            for player in roster: 
                cursor.execute(post_roster_queries[videogame], (school, player))

            return jsonify({"message": "Roster created successfully."}), 200

        except Exception as e: 
            print(e)
            return jsonify({"error": str(e)}), 500
        
        finally: 
            conn.commit()
            cursor.close()
            conn.close()

    elif request.method == "DELETE": 
        data = request.get_json()
        school = data.get('school')

        try: 
            delete_roster_queries = { 
                "rl": "DELETE FROM rl_roster WHERE school = %s",
                "val": "DELETE FROM val_roster WHERE school = %s",
                "apex": "DELETE FROM apex_roster WHERE school = %s"
            }

            cursor.execute(delete_roster_queries[videogame], (school,))

            return jsonify({"message": "Roster deleted successfully."}), 200

        except Exception as e: 
            print(e)
            return jsonify({"error": str(e)}), 500
        
        finally: 
            conn.commit()
            cursor.close()
            conn.close()