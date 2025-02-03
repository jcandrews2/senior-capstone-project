from flask import Blueprint, jsonify, request
import pymysql
import bcrypt
from db import get_db_connection

login_bp = Blueprint('login', __name__)
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    data = request.get_json()  # Parse the JSON body of the request
    username = data.get('username')
    password = data.get('password')

    print(username, password)
    try: 
        cursor.execute( 
            "SELECT * from users WHERE username = %s", (username,)
        )

        user = cursor.fetchone()

        if user: 
            if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')): 
                return jsonify({"username": user["username"], "isAdmin": bool(user["is_admin"])}, 200)

            else: 
                return jsonify({"error": "Invalid credentials"}), 401
        else: 
            return jsonify({"error": "Username not found."}), 404

    except Exception as e: 
        print(e)
        return jsonify({"error": str(e)}), 500
    
    finally: 
        cursor.close()
        conn.close()
