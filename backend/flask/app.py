from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)

# db config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'afkuser'
app.config['MYSQL_PASSWORD'] = 'afk'
app.config['MYSQL_DB'] = 'SCAC_STATS'

from login import login_bp
from account import account_bp
from upload import upload_bp
from stats import stats_bp
from player import player_bp
from disputes import disputes_bp

app.register_blueprint(login_bp)
app.register_blueprint(account_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(player_bp)
app.register_blueprint(disputes_bp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
