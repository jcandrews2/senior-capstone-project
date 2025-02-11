from flask import Blueprint, jsonify, request
import pymysql
from urllib.parse import unquote
from db import get_db_connection

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/match_stats/<videogame>', methods=['GET'])
def get_match_stats(videogame):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    data = request.args.get('week')
    week = unquote(data)

    if week == 'avg':
        return jsonify({"message": "bad request"}), 400

    # Queries for getting matchup list
    matchup_queries = { 
        "rl": "SELECT DISTINCT school, team_score, opponent, opponent_score FROM rl_week WHERE week_number = %s AND did_win = TRUE",
        "val": "SELECT DISTINCT school, team_score, opponent, opponent_score FROM val_week WHERE week_number = %s AND did_win = TRUE",
        "apex": "SELECT DISTINCT school FROM apex_week WHERE week_number = %s;"
    }

    # Game queries
    game_queries = {
        "rl": {
            "game_query": """
                SELECT game_id, game_number, w_school, l_school, w_points, l_points
                FROM rl_picture
                WHERE week_number = %s AND w_school = %s
                GROUP BY game_id
                ORDER BY game_number;
            """,
            "player_query": """
                SELECT school, player_name AS `player`, score, goals, assists, saves, shots
                FROM rl_game
                WHERE game_id = %s
            """
        },
        "val": {
            "game_query": """
                SELECT game_id, game_number, w_school, l_school, w_points, l_points
                FROM val_picture
                WHERE week_number = %s AND w_school = %s
                GROUP BY game_id
                ORDER BY game_number

            """,
            "player_query": """
                SELECT school, player_name AS `player`, combat_score AS `combat score` , kills, deaths, assists, econ, fb, plants, defuses, agent, map
                FROM val_game
                WHERE game_id = %s
            """
        },
        "apex": {
            "game_query": """
                SELECT school, game_number, game_id
                FROM apex_picture
                WHERE week_number = %s AND school = %s
                GROUP BY game_id
                ORDER BY game_number
            """,
            "player_query": """
                SELECT school, player_name AS `player`, placement, kills, assists, knocks, damage, score
                FROM apex_game
                WHERE game_id = %s AND school = %s
            """
        }
    }

    week_queries = { 
        "rl": "SELECT school, player_name AS `player`, week_score_avg, week_goals_avg, week_assists_avg, week_saves_avg, week_shots_avg FROM rl_week WHERE week_number = %s AND (school = %s OR school = %s)",
        "val": "SELECT school, player_name AS `player`, week_cs_avg, week_kills_avg, week_deaths_avg, week_assists_avg, week_econ_avg, week_fb_avg, week_plants_avg, week_defuses_avg FROM val_week WHERE week_number = %s AND (school = %s OR school = %s)",
        "apex": "SELECT school, player_name AS `player`,  week_kills_avg, week_assists_avg, week_knocks_avg, week_damage_avg, week_kills, week_assists, week_knocks, week_damage, week_score FROM apex_week WHERE week_number = %s AND school = %s"
    }

    try:
        if videogame not in game_queries:
            return jsonify({"error": f"Game '{videogame}' is not supported"}), 400

        # Get the matchups
        cursor.execute(matchup_queries[videogame], (week,))
        matchups = cursor.fetchall()
        
        response = []

        for matchup in matchups:

            if videogame == "apex": 

                # Get the school
                school = matchup['school']

                # Get weekly stats
                cursor.execute(week_queries[videogame], (week, school))
                week_stats = cursor.fetchall()

                match_data = { 
                    "match" : { 
                        "school": school,
                        "points" : 0,
                        "games": []
                    },
                    "week" : week_stats
                }
                
                cursor.execute(game_queries[videogame]["game_query"], (week, school))
                games = cursor.fetchall()

               
                for game in games: 

                    cursor.execute(game_queries[videogame]["player_query"], (game['game_id'], school))
                    player_stats = cursor.fetchall()

                    
                    team_stats = []

                    for player in player_stats: 
                        team_stats.append(player)
                        
                        
                    game_data = {
                        "gameStats": {
                            "school": school,
                            "points": player['score'],
                            "gameNumber": game["game_number"],
                            "gameID": game['game_id']
                        },
                        "teamStats": team_stats,
                    }
                    cursor.execute(f"""SELECT week_score from apex_week
                                   WHERE week_number = {week} and school = '{school}'
                                   GROUP BY school;""")
                    week_points = cursor.fetchone()["week_score"]
                    
                    match_data["match"]['points'] = week_stats[0]["week_score"]
                    #match_data["match"]['points'] = match_points
                    match_data["match"]['games'].append(game_data)

            else: 
                # Get the matchup
                school, opponent = matchup['school'], matchup['opponent']

                # Get weekly stats
                cursor.execute(week_queries[videogame], (week, school, opponent))
                week_stats = cursor.fetchall()

                # Format the match data
                match_data = { 
                    "match" : { 
                        "school": school,
                        "opponent": opponent,
                        "teamScore": matchup['team_score'],
                        "opponentScore": matchup["opponent_score"],
                        "games": []
                    },
                "week" : week_stats
                }
                
                # Get the match's games
                cursor.execute(game_queries[videogame]["game_query"], (week, school))
                games = cursor.fetchall()

                # Go thru the games and get player data
                for game in games: 

                    # Get the player stats
                    cursor.execute(game_queries[videogame]["player_query"], (game['game_id'],))
                    player_stats = cursor.fetchall()

                    team_stats = [player for player in player_stats if player['school'] == school]
                    opponent_stats = [player for player in player_stats if player['school'] == opponent]

                    game_data = {
                        "gameStats": {
                            "school": school,
                            "opponent": opponent,
                            "teamScore": game["w_points"],
                            "opponentScore": game["l_points"],
                            "gameNumber": game["game_number"],
                            "gameID": game['game_id']
                        },
                        "teamStats": team_stats,
                        "opponentStats": opponent_stats
                    }

                    match_data["match"]['games'].append(game_data)

            response.append(match_data)

        return jsonify(response)
    
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

@stats_bp.route('/season_stats/<videogame>', methods=['GET'])
def get_season_stats(videogame):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    data = request.args.get('week')
    week = unquote(data)

    if week != 'avg': 
        return jsonify({"message": "bad request"}), 400

    try:
        cursor.execute("SELECT DISTINCT school FROM users;")
        schools = cursor.fetchall()

        season_queries = { 
            "rl":  "SELECT school, player_name AS `player`, season_score_avg, season_goals_avg, season_assists_avg, season_saves_avg, season_shots_avg FROM rl_season WHERE school = %s",
            "val": "SELECT school, player_name AS `player`, season_cs_avg, season_kills_avg, season_deaths_avg, season_assists_avg, season_econ_avg, season_fb_avg, season_plants_avg, season_defuses_avg FROM val_season WHERE school = %s",
            "apex": "SELECT school, player_name AS `player`, season_kills_avg, season_assists_avg, season_knocks_avg, season_damage_avg, total_kills, total_assists, total_damage, total_score FROM apex_season WHERE school = %s"
        }
        
        response = []
        for school in schools:
                school_name = school.get("school")
                if school_name != "None":
                    cursor.execute(season_queries[videogame], (school_name,))
                    results = cursor.fetchall()
                    response.append({"school": school_name, "players": results})
            
        return jsonify(response), 200


    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()