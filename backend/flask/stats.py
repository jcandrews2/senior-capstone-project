from flask import Blueprint, jsonify, request
import pymysql
from urllib.parse import unquote
from db import get_db_connection

stats_bp = Blueprint('stats', __name__)

@stats_bp.route('/stats/<videogame>', methods=['GET'])
def get_game_stats(videogame):
    conn = get_db_connection()
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    data = request.args.get('week')
    week = unquote(data)

    # Queries for getting matchup list
    matchup_queries = { 
        "rl": "SELECT DISTINCT school, team_score, opponent, opponent_score FROM rl_week WHERE week_number = %s AND did_win = TRUE",
        "val": "SELECT DISTINCT school, team_score, opponent, opponent_score FROM val_week WHERE week_number = %s AND and did_win = TRUE",
        "apex": "SELECT DISTINCT school FROM apex_week WHERE week_number = %s;"
    }

    # Game queries
    game_queries = {
        "rl": {
            "game_query": """
                SELECT game_id, game_number, w_school, l_school, w_points, l_points
                FROM rl_picture
                WHERE week_number = %s AND (w_school = %s OR l_school)
                GROUP BY game_id
                ORDER BY game_number;
            """,
            "player_query": """
                SELECT school, player_name, score, goals, assists, saves, shots
                FROM rl_game
                WHERE game_id = %s;
            """
        },
        "val": {
            "game_query": """
                SELECT game_id, game_number, w_school, l_school, w_points, l_points
                FROM val_game
                WHERE week_number = %s AND AND (w_school = %s OR l_school)
                ORDER BY game_number;
            """,
            "player_query": """
                SELECT school, player_name, combat_score, kills, deaths, assists, econ, fb, plants, defuses, score
                FROM val_game
                WHERE game_id = %s AND school = %s;
            """
        },
        "apex": {
            "game_query": """
                SELECT school, game_number, game_id
                FROM apex_picture
                WHERE week_number = %s AND school = %s
                GROUP BY game_id
                ORDER BY game_number;
            """,
            "player_query": """
                SELECT school, player_name, placement, kills, assists, knocks, damage, score 
                FROM apex_game
                WHERE game_id = %s AND school = %s;
            """
        }
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

                match_data = { 
                    "match" : { 
                        "school": school,
                        "points" : 0,
                        "games": []
                    },
                    "average" : { 
                        # will put weekly avg here
                    }
                }
                
                cursor.execute(game_queries[videogame]["game_query"], (week, school))
                games = cursor.fetchall()

                
                match_points = 0
                for game in games: 

                    cursor.execute(game_queries[videogame]["player_query"], (game['game_id'], school))
                    player_stats = cursor.fetchall()

                    game_points = 0
                    team_stats = []

                    for player in player_stats: 
                        if player['placement'] == 1: 
                            game_points += 12
                        elif player['placement'] == 2: 
                            game_points += 9
                        elif player['placement'] == 3: 
                            game_points += 7
                        elif player['placement'] == 4:
                            game_points += 5 
                        elif player['placement'] == 5: 
                            game_points += 4
                        elif player['placement'] <= 7: 
                            game_points += 3
                        elif player['placement'] <= 10: 
                            game_points += 2
                        elif player['placement'] <= 15: 
                            game_points += 1

                        game_points += player['kills']
                        game_points += player['damage'] % 200
                        
                        team_stats.append(player)

                    match_points += game_points
       
                        
                    game_data = {
                        "gameStats": {
                            "school": school,
                            "points": game_points,
                            "gameNumber": game["game_number"]
                        },
                        "teamStats": team_stats,
                    }

                    match_data["match"]['points'] = match_points
                    match_data["match"]['games'].append(game_data)

            else: 
                # Get the matchup
                school, opponent = matchup['school'], matchup['opponent']

                # Format the match data
                match_data = { 
                    "match" : { 
                        "school": school,
                        "opponent": opponent,
                        "teamScore": matchup['team_score'],
                        "opponentScore": matchup["opponent_score"],
                        "games": []
                    },
                   "average" : { 
                        # will put weekly avg here
                    }
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
                            "gameNumber": game["game_number"]
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
