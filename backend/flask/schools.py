from flask import Blueprint, jsonify, request
import pymysql
from urllib.parse import unquote
from db import get_db_connection

schools_bp = Blueprint('schools', __name__)

@schools_bp.route('/schools', methods=['GET'])
def schools():
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    try:
        cursor.execute('SELECT school FROM users WHERE school != "None" GROUP BY school ')
    
        schools = [school['school'] for school in cursor.fetchall()]

        return jsonify(schools), 200


    except Exception as e: 
        print(e)
        return jsonify({"error": str(e)}), 500
    
    finally: 
        cursor.close()
        conn.close()