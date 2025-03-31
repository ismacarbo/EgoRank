import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import math
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_dance.contrib.google import make_google_blueprint, google
from datetime import date

app = Flask(__name__)
app.secret_key = 'la_tua_chiave_segreta'

# Configurazione MongoDB (assicurati che MongoDB sia in esecuzione)
app.config["MONGO_URI"] = "mongodb://localhost:27017/ego_rank_db"
mongo = PyMongo(app)

# Configurazione Flask-Login
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Configurazione Flask-Dance per Google OAuth con scope aggiornati
google_bp = make_google_blueprint(
    client_id="289731328884-dld5r01gflkbnaq6egao74icoc44d08v.apps.googleusercontent.com",
    client_secret="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",
    scope=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
    redirect_url="http://localhost:5000/login/google/authorized"
)

app.register_blueprint(google_bp, url_prefix="/login")

def get_title(score):
    if score < 50:
        return "Novizio"
    elif score < 100:
        return "Gladiatore"
    elif score < 150:
        return "Campione"
    else:
        return "Eroe"

def next_threshold(score):
    if score < 50:
        return 50
    elif score < 100:
        return 100
    elif score < 150:
        return 150
    else:
        return None

# Classe User per Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.username = user_data.get('username')
        self.email = user_data.get('email')
        self.experience = user_data.get('experience')
        self.gender = user_data.get('gender')
        self.weight = user_data.get('weight')
        self.age = user_data.get('age')
        self.lifts = user_data.get('lifts', {'bench': 0, 'squat': 0, 'deadlift': 0})
        self.coins = user_data.get('coins', 0)
        self.last_workout = user_data.get('last_workout')

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Rotta home (landing page)
@app.route("/")
def index():
    return render_template("index.html")

# Registrazione
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username   = request.form.get("username")
        email      = request.form.get("email")
        password   = request.form.get("password")
        experience = request.form.get("experience")
        gender     = request.form.get("gender")
        weight     = request.form.get("weight")
        age        = request.form.get("age")
        
        # Verifica se esiste già un utente con lo stesso username
        if mongo.db.users.find_one({"username": username}):
            flash("Username già esistente, scegline un altro")
            return redirect(url_for("register"))
        
        hashed_password = generate_password_hash(password, method="pbkdf2:sha256", salt_length=8)
        
        try:
            exp_int = int(experience)
        except:
            exp_int = 0
        lifts = {
            "bench": exp_int * 10,
            "squat": exp_int * 9,
            "deadlift": exp_int * 11
        }
        
        user_doc = {
            "username": username,
            "email": email,
            "password": hashed_password,
            "experience": experience,
            "gender": gender,
            "weight": weight,
            "age": age,
            "lifts": lifts,
            "coins": 0,             # Nuovo campo: saldo iniziale di monete
            "last_workout": None    # Campo per tracciare il completamento giornaliero
        }
        mongo.db.users.insert_one(user_doc)
        flash("Registrazione completata, adesso effettua il login")
        return redirect(url_for("login"))
    return render_template("register.html")

# Login con username e password
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_doc = mongo.db.users.find_one({"username": username})
        if user_doc and check_password_hash(user_doc["password"], password):
            user = User(user_doc)
            login_user(user)
            flash("Accesso effettuato correttamente")
            return redirect(url_for("dashboard"))
        else:
            flash("Username o password errati")
            return redirect(url_for("login"))
    return render_template("login.html")

# Login con Google
@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Errore durante il recupero delle informazioni da Google")
        return redirect(url_for("login"))
    google_info = resp.json()
    email = google_info.get("email")
    username = google_info.get("name")
    user_doc = mongo.db.users.find_one({"email": email})
    if not user_doc:
        user_doc = {
            "username": username,
            "email": email,
            "password": None,
            "experience": "0",
            "gender": "",
            "weight": "0",
            "age": "0",
            "lifts": {"bench": 0, "squat": 0, "deadlift": 0},
            "coins": 0,
            "last_workout": None
        }
        result = mongo.db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
    user = User(user_doc)
    login_user(user)
    flash("Accesso con Google effettuato correttamente")
    return redirect(url_for("dashboard"))

# Logout
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout effettuato correttamente")
    return redirect(url_for("index"))

# Dashboard: visualizza le informazioni personali e una classifica globale (es. basata sul Bench Press)
@app.route("/dashboard")
@login_required
def dashboard():
    users_cursor = mongo.db.users.find()
    ranking_users = []
    for u in users_cursor:
        score = u.get("lifts", {}).get("bench", 0)
        ranking_users.append({
            "username": u.get("username"),
            "score": score,
            "title": get_title(score)
        })
    ranking_users = sorted(ranking_users, key=lambda x: x["score"], reverse=True)
    return render_template("dashboard.html", ranking_users=ranking_users)

# Pagina per gestire le progressioni settimanali per ciascun esercizio
@app.route("/exercise", methods=["GET", "POST"])
@login_required
def exercise():
    exercise_type = request.args.get("exercise", "bench")
    if exercise_type not in ["bench", "squat", "deadlift"]:
        exercise_type = "bench"
    forecast_message = None
    user_doc = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
    
    if request.method == "POST":
        increment = request.form.get("increment")
        try:
            increment = float(increment)
        except Exception:
            increment = 0
        current_score = user_doc.get("lifts", {}).get(exercise_type, 0)
        new_score = current_score + increment
        mongo.db.users.update_one(
            {"_id": ObjectId(current_user.id)},
            {"$set": {f"lifts.{exercise_type}": new_score}}
        )
        user_doc = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
        nt = next_threshold(new_score)
        if nt is not None and increment > 0:
            weeks = math.ceil((nt - new_score) / increment)
            forecast_message = (
                f"Con un incremento settimanale di {increment}, "
                f"raggiungerai il prossimo rango ({get_title(nt)}) in circa {weeks} settimana(e)."
            )
        else:
            forecast_message = "Hai raggiunto il rango massimo o l'incremento inserito non permette una previsione."
    
    users_cursor = mongo.db.users.find()
    ranking_users = []
    for u in users_cursor:
        score = u.get("lifts", {}).get(exercise_type, 0)
        ranking_users.append({
            "username": u.get("username"),
            "score": score,
            "title": get_title(score)
        })
    ranking_users = sorted(ranking_users, key=lambda x: x["score"], reverse=True)
    
    return render_template("exercise.html",
                           exercise_type=exercise_type,
                           ranking_users=ranking_users,
                           forecast_message=forecast_message)

# (Opzionale) API per ottenere la classifica globale (esempio basato sul Bench)
@app.route("/api/rankings")
def rankings():
    users_cursor = mongo.db.users.find()
    ranking_users = []
    for u in users_cursor:
        score = u.get("lifts", {}).get("bench", 0)
        ranking_users.append({
            "username": u.get("username"),
            "score": score,
            "title": get_title(score)
        })
    ranking_users = sorted(ranking_users, key=lambda x: x["score"], reverse=True)
    return jsonify(ranking_users)

# Nuova rotta per il workout giornaliero
@app.route("/daily_workout", methods=["GET", "POST"])
@login_required
def daily_workout():
    today = date.today().isoformat()
    user_doc = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
    workout_completed = (user_doc.get("last_workout") == today)
    
    if request.method == "POST":
        if not workout_completed:
            coins_reward = 10
            new_coins = user_doc.get("coins", 0) + coins_reward
            mongo.db.users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$set": {"coins": new_coins, "last_workout": today}}
            )
            flash(f"Workout completato! Hai guadagnato {coins_reward} monete.")
            return redirect(url_for("daily_workout"))
        else:
            flash("Hai già completato il workout di oggi.")
            return redirect(url_for("daily_workout"))
    
    return render_template("daily_workout.html", workout_completed=workout_completed)

if __name__ == "__main__":
    app.run(debug=True)
