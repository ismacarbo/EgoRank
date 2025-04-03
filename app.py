import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
import math
import random
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_pymongo import PyMongo
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
from flask_dance.contrib.google import make_google_blueprint, google
from datetime import date

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MongoDB configuration
app.config["MONGO_URI"] = "mongodb://localhost:27017/ego_rank_db"
mongo = PyMongo(app)

# Flask-Login configuration
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Flask-Dance configuration for Google OAuth
google_bp = make_google_blueprint(
    client_id="289731328884-dld5r01gflkbnaq6egao74icoc44d08v.apps.googleusercontent.com",
    client_secret="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",
    scope=["openid", "https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email"],
    redirect_url="http://localhost:5000/login/google/authorized"
)
app.register_blueprint(google_bp, url_prefix="/login")

def get_title(score):
    if score < 50:
        return "Novice"
    elif score < 100:
        return "Gladiator"
    elif score < 150:
        return "Champion"
    else:
        return "Hero"

def next_threshold(score):
    if score < 50:
        return 50
    elif score < 100:
        return 100
    elif score < 150:
        return 150
    else:
        return None

def compute_level(xp):
    level = xp // 100 + 1
    current_level_xp = xp % 100
    xp_to_next = 100 - current_level_xp
    progress = (current_level_xp / 100) * 100
    return level, progress, xp_to_next

def get_exercises(muscle):
    API_KEY = "YOUR_API_KEY"  # Sostituisci con la tua chiave API effettiva
    headers = {'X-Api-Key': API_KEY}
    api_url = f'https://api.api-ninjas.com/v1/exercises?muscle={muscle}'
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        exercises = response.json()
        if len(exercises) > 3:
            exercises = random.sample(exercises, 3)
        return exercises
    else:
        print("Error fetching exercises for", muscle, response.status_code, response.text)
        return []

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
        self.xp = user_data.get('xp', 0)
        self.last_workout = user_data.get('last_workout')

@login_manager.user_loader
def load_user(user_id):
    user_data = mongo.db.users.find_one({"_id": ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

@app.route("/")
def index():
    return render_template("index.html")

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
        
        if mongo.db.users.find_one({"username": username}):
            flash("Username already exists, please choose another.")
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
            "coins": 0,
            "xp": 0,
            "last_workout": None
        }
        mongo.db.users.insert_one(user_doc)
        flash("Registration successful! Please log in.")
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user_doc = mongo.db.users.find_one({"username": username})
        if user_doc and check_password_hash(user_doc["password"], password):
            user = User(user_doc)
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for("dashboard"))
        else:
            flash("Incorrect username or password.")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/google_login")
def google_login():
    if not google.authorized:
        return redirect(url_for("google.login"))
    resp = google.get("/oauth2/v2/userinfo")
    if not resp.ok:
        flash("Error retrieving information from Google.")
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
            "xp": 0,
            "last_workout": None
        }
        result = mongo.db.users.insert_one(user_doc)
        user_doc["_id"] = result.inserted_id
    user = User(user_doc)
    login_user(user)
    flash("Logged in with Google successfully.")
    return redirect(url_for("dashboard"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out successfully.")
    return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    users_cursor = mongo.db.users.find()
    ranking_users = []
    for u in users_cursor:
        score = u.get("lifts", {}).get("bench", 0)
        xp = u.get("xp", 0)
        level, _, _ = compute_level(xp)
        ranking_users.append({
            "username": u.get("username"),
            "score": score,
            "title": get_title(score),
            "level": level
        })
    ranking_users = sorted(ranking_users, key=lambda x: x["score"], reverse=True)
    
    current_level, progress, xp_to_next = compute_level(current_user.xp)
    
    return render_template("dashboard.html", ranking_users=ranking_users, level=current_level, progress=progress, xp_to_next=xp_to_next)

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
        nt = next_threshold(new_score)
        if nt is not None and increment > 0:
            weeks = math.ceil((nt - new_score) / increment)
            forecast_message = (
                f"With a weekly increment of {increment}, you'll reach the next rank ({get_title(nt)}) in about {weeks} week(s)."
            )
        else:
            forecast_message = "You've reached the maximum rank or the entered increment doesn't allow a prediction."
    
    users_cursor = mongo.db.users.find()
    ranking_users = []
    for u in users_cursor:
        score = u.get("lifts", {}).get(exercise_type, 0)
        xp = u.get("xp", 0)
        level, _, _ = compute_level(xp)
        ranking_users.append({
            "username": u.get("username"),
            "score": score,
            "title": get_title(score),
            "level": level
        })
    ranking_users = sorted(ranking_users, key=lambda x: x["score"], reverse=True)
    
    current_level, progress, xp_to_next = compute_level(current_user.xp)
    
    return render_template("exercise.html",
                           exercise_type=exercise_type,
                           ranking_users=ranking_users,
                           forecast_message=forecast_message,
                           level=current_level,
                           progress=progress,
                           xp_to_next=xp_to_next)

@app.route("/daily_workout", methods=["GET", "POST"])
@login_required
def daily_workout():
    today = date.today().isoformat()
    user_doc = mongo.db.users.find_one({"_id": ObjectId(current_user.id)})
    workout_completed = (user_doc.get("last_workout") == today)
    
    if request.method == "POST":
        if not workout_completed:
            coins_reward = 10
            xp_reward = 10
            new_coins = user_doc.get("coins", 0) + coins_reward
            new_xp = user_doc.get("xp", 0) + xp_reward
            mongo.db.users.update_one(
                {"_id": ObjectId(current_user.id)},
                {"$set": {"coins": new_coins, "xp": new_xp, "last_workout": today}}
            )
            flash(f"Workout completed! You earned {coins_reward} coins and {xp_reward} XP.")
            return redirect(url_for("daily_workout"))
        else:
            flash("You have already completed today's workout.")
            return redirect(url_for("daily_workout"))
    
    selected_muscle = request.args.get("muscle")
    allowed_muscles = ["chest", "back", "biceps", "triceps", "legs", "shoulders", "abs"]
    exercises = None
    if not selected_muscle or selected_muscle.lower() not in allowed_muscles:
        show_selection = True
    else:
        show_selection = False
        exercises = get_exercises(selected_muscle.lower())
    
    return render_template("daily_workout.html", workout_completed=workout_completed, exercises=exercises, show_selection=show_selection, allowed_muscles=allowed_muscles)

@app.route("/progressions")
@login_required
def progressions():
    # Mappiamo i gruppi muscolari dai dati dell'utente
    muscle_progress = {
         "chest": current_user.lifts.get("bench", 0),
         "legs": current_user.lifts.get("squat", 0),
         "back": current_user.lifts.get("deadlift", 0),
         "biceps": 0,
         "triceps": 0,
         "shoulders": 0,
         "abs": 0
    }
    muscle_ranks = {}
    for muscle, score in muscle_progress.items():
         if score > 0:
             muscle_ranks[muscle] = get_title(score)
         else:
             muscle_ranks[muscle] = "rank ancora da effettuare"
    
    return render_template("progressions.html", muscle_ranks=muscle_ranks, gender=current_user.gender)

if __name__ == "__main__":
    app.run(debug=True)
