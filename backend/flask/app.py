from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mail import Message, Mail
import secrets

app = Flask(__name__)
app.json.sort_keys = False
CORS(app)
# Allow CORS for any domain
# CORS(app, resources={r"/api/*": {"origins": "*"}})


# db config
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'afkuser'
app.config['MYSQL_PASSWORD'] = 'afk'
app.config['MYSQL_DB'] = 'SCAC_STATS'

# Configure Flask-Mail settings
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'afk.scac@gmail.com'
app.config['MAIL_PASSWORD'] = 'hvqa sfsc cdkh yjac'
app.config['MAIL_DEFAULT_SENDER'] = 'afk.scac@gmail.com'

from login import login_bp
from account import account_bp
from upload import upload_bp
from stats import stats_bp
from player import player_bp
from disputes import disputes_bp
from roster import roster_bp
from schools import schools_bp
from rankings import rankings_bp
from retrieve import retrieve_bp

app.register_blueprint(login_bp)
app.register_blueprint(account_bp)
app.register_blueprint(upload_bp)
app.register_blueprint(stats_bp)
app.register_blueprint(player_bp)
app.register_blueprint(disputes_bp)
app.register_blueprint(roster_bp)
app.register_blueprint(schools_bp)
app.register_blueprint(rankings_bp)
app.register_blueprint(retrieve_bp)

mail = Mail(app)

def generate_passkey(length=8):
    return secrets.token_urlsafe(length)

@app.route('/send', methods=['POST'])
def send_email():
    data = request.get_json()
    email = data.get('email') 

    passkey = generate_passkey()

    msg = Message("AFK Esports Forgot Password", recipients=[email])
    msg.body = f"Passkey: {passkey}"

    try:
        mail.send(msg)
        return jsonify({"passkey": passkey}), 200
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=True)
