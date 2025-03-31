# 💪 Ego Rank

**Ego Rank** is a gamified web app for gym lovers. It lets you track and compare your main lifts (bench press, squat, deadlift) with your friends in a public leaderboard with themed titles like *Novice*, *Gladiator*, *Champion*, and *Hero*.  
Each user can monitor their progress, receive weekly progression forecasts, and log in using classic credentials or Google OAuth.

---

## 🚀 Features

- 👤 Registration and login (username/password + Google OAuth)
- 📊 Manage lifts per exercise (bench, squat, deadlift)
- 🏆 Public leaderboard for each exercise
- 🔮 Weekly progression forecasts with estimated time to next rank
- 🔐 Account and data stored in MongoDB
- 📈 Personal dashboard with ranking view

---

## 🛠️ Technologies Used

- **Flask** - Web backend framework (Python)
- **MongoDB** - NoSQL database for data storage
- **Flask-Login** - Session and user management
- **Flask-Dance** - Google OAuth integration
- **Werkzeug** - Secure password hashing
- **Bootstrap 4** - Responsive and clean UI

---

## 📦 Local Installation & Setup

### Prerequisites

- Python 3.8+ (recommended)
- MongoDB running locally (`mongodb://localhost:27017`)
- Google Client ID and Secret for OAuth 2.0

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ego-rank.git
   cd ego-rank
   ```

2. **Install the dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google OAuth**

   Register your app at [Google Developers Console](https://console.developers.google.com/) and get:

   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

   Add them in `app.py`:
   ```python
   client_id="YOUR_GOOGLE_CLIENT_ID",
   client_secret="YOUR_GOOGLE_CLIENT_SECRET",
   ```

4. **Run the Flask server**
   ```bash
   python app.py
   ```

5. **Open in your browser**
   ```
   http://127.0.0.1:5000
   ```

---

## 📁 Main Files

| File/Folder           | Description                                      |
|-----------------------|--------------------------------------------------|
| `app.py`              | Flask server logic and routing                   |
| `templates/`          | HTML pages rendered by Flask                     |
| `static/`             | (optional) Custom CSS/JS files                   |
| `README.md`           | Project documentation                            |
| `requirements.txt`    | Python dependencies                              |

---

## ✍️ Contributing

To contribute:

1. Fork the project
2. Create a new branch (`git checkout -b feat-new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to your fork (`git push origin feat-new-feature`)
5. Open a Pull Request 🚀

---

## 📄 License

This project is open-source and released under the **MIT License**.

---

## 🙏 Credits

Special thanks to all gym enthusiasts who treat their progress like a game: **Ego Rank** is for you.

---

## ✨ Short Description for GitHub

> A gamified web app for gym users to rank their lifts (bench, squat, deadlift), forecast progress, and log in via Google or username/password. 💪
