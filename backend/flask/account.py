from flask import Blueprint, jsonify, request
import pymysql
import pymysql
from db import get_db_connection
import bcrypt

account_bp = Blueprint('account', __name__)

@account_bp.route('/accounts', methods=['GET', 'POST', 'PUT', 'DELETE'])
def accounts():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    if request.method == 'GET': 
        try: 
            cursor.execute( 
                "SELECT * from users WHERE is_admin = 0"
            )

            response = []

            users = cursor.fetchall()

            for user in users: 

                user_info = { 
                    "username": user.get("username"),
                    "school": user.get("school"),
                }

                response.append(user_info)

            return jsonify(response), 200


        except Exception as e: 
            print(e)
            return jsonify({"error": str(e)}), 500
        
        finally: 
            cursor.close()
            conn.close()

    elif request.method == 'POST':

        data = request.get_json()
        school = data.get('shool')
        username = data.get('username')
        password = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()).decode('UTF-8')

        try: 
            cursor.execute ( 
                "INSERT INTO users (school, username, password, is_admin) VALUES (%s, %s, %s, 0)", (school, username, password)
            )

            return jsonify({"message": "Account created successfully."}), 200

        except Exception as e: 
            return jsonify({"error": str(e)}), 500
        
        finally: 
            conn.commit()
            cursor.close()
            conn.close()

    elif request.method == 'PUT': 

        data = request.get_json()
        username = data.get('username')
        password = bcrypt.hashpw(data.get('password').encode('utf-8'), bcrypt.gensalt()).decode('UTF-8')

        try: 
            cursor.execute ( 
                "UPDATE users SET password = %s WHERE username = %s", (password, username)
            )

            return jsonify({"message": "User password updated successfully."}), 200

        except Exception as e: 
            return jsonify({"error": str(e)}), 500
        
        finally: 
            conn.commit()
            cursor.close()
            conn.close()

    elif request.method == 'DELETE': 

        data = request.get_json()
        username = data.get('username')

        try: 
            cursor.execute ( 
                "DELETE FROM users WHERE username = %s", (username,)
            )

            return jsonify({"message": "Account deleted successfully."}), 200

        except Exception as e: 
            return jsonify({"error": str(e)}), 500
        
        finally: 
            conn.commit()
            cursor.close()
            conn.close()
