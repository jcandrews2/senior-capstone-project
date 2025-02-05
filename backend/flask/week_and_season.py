import re
from flask import Blueprint, jsonify, request
import pymysql
from db import get_db_connection
import os
import subprocess
import json
import uuid

week_and_season_bp = Blueprint('week_and_season', __name__)

@week_and_season_bp.route('/update_week_and_season/<videogame>', methods=['GET', 'PUT', 'POST'])
def update_week_and_season(videogame):
        
    conn = get_db_connection()
    cursor = conn.cursor()

    try: 
        #for each player run
        if request.method == "GET": 
            data = request.get_json()
            player = data.get('player')
            
            // 
            get_week_queries = { 
                "rocket-league": "SELECT player FROM rl_week WHERE player_name = %s",
                "valorant": "",
                "apex-legends: ""  
            }
            
            # execute the query for the player
            
        return jsonify({player}), 200
    
    except Exception as e:
        conn.rollback()  # 🔹 Rollback if error occurs
        print(f"Error uploading match data: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        cursor.close()
        conn.close()
    
        
    
    elif request.method == "POST": 
        try: 
            # inser the data
            insert_week_and_season_queries = { 
                "rocket-league": """
                    INSERT INTO rl_picture (
                        game_id, game_number, week_number, w_school, l_school, w_points, l_points, picture)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
                    """,
                "valorant": """
                    INSERT INTO val_week(week_number, school, player_name, week_cs_avg, week_kills_avg, week_deaths_avg, week_assists_avg, week_econ_avg, week_fb_avg, week_plants_avg, week_defuses_avg, team_score)
                    SELECT week_number, school, player_name, AVG(combat_score), AVG(kills), AVG(deaths), AVG(assists), AVG(econ), AVG(fb), AVG(plants), AVG(defuses), sum(did_win)
                    FROM val_game
                    WHERE player_name= %s and week_number= %s
                    GROUP BY week_number, school, player_name;

                    UPDATE val_week
                    SET val_week.did_win = IF((val_week.team_score) < 2, FALSE, TRUE)
                    WHERE val_week.player_name = 'p1' and val_week.week_number =1;

                    UPDATE val_week
                    SET val_week.opponent_score = (
                    SELECT sum(did_win)
                    FROM val_game
                    WHERE val_game.player_name = 'opponent' AND rl_game.week_number = 1
                    )
                    WHERE val_week.player_name = 'p1’ AND rl_week.week_number = 1 ; 
                    """,
                "apex-legends": """
                    INSERT INTO rl_picture (
                        game_id, game_number, week_number, picture)
                    VALUES (%s, %s, %s, %s);
                    """,                       
                }
            pass
            
        except Exception as e:
            conn.rollback()  # 🔹 Rollback if error occurs
            print(f"Error uploading match data: {e}")
            return jsonify({"error": str(e)}), 500

        finally:
            cursor.close()
            conn.close()
            
        
    elif request.method == "PUT": 
        try: 
            # udpdate the data
            pass
            
        except Exception as e:
            conn.rollback()  # 🔹 Rollback if error occurs
            print(f"Error uploading match data: {e}")
            return jsonify({"error": str(e)}), 500

        finally:
            cursor.close()
            conn.close()


        