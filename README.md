# 💪 Ego Rank

**Ego Rank** è una web app gamificata per chi va in palestra: permette di confrontare i propri sollevamenti (bench press, squat, deadlift) con quelli degli amici in una classifica a tema "rank", con titoli come *Novizio*, *Gladiatore*, *Campione* ed *Eroe*.  
Ogni utente può tenere traccia dei propri progressi, ricevere previsioni sul tempo stimato per salire di rango e accedere tramite login classico o Google.

---

## 🚀 Funzionalità

- 👤 Registrazione e login (username/password + Google OAuth)
- 📊 Gestione dei sollevamenti per esercizio (bench, squat, deadlift)
- 🏆 Classifiche pubbliche per ogni esercizio
- 🔮 Previsioni di progressione settimanale con stima del prossimo rango
- 🔐 Account e dati salvati su database MongoDB
- 📈 Dashboard personale con visualizzazione ranking

---

## 🛠️ Tecnologie utilizzate

- **Flask** - Backend web framework (Python)
- **MongoDB** - Database NoSQL per la persistenza dei dati
- **Flask-Login** - Gestione delle sessioni utente
- **Flask-Dance** - Integrazione con Google OAuth
- **Werkzeug** - Hashing sicuro delle password
- **Bootstrap 4** - Interfaccia responsive e pulita

---

## 📦 Installazione e avvio (locale)

### Prerequisiti

- Python 3.8+ (consigliato)
- MongoDB attivo in locale (`mongodb://localhost:27017`)
- Client ID e Secret di Google per OAuth 2.0

### Passaggi

1. **Clona la repository**
   ```bash
   git clone https://github.com/tuo-utente/ego-rank.git
   cd ego-rank
   ```

2. **Installa le dipendenze**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura Google OAuth**

   Registra la tua app su [Google Developers Console](https://console.developers.google.com/) e ottieni:

   - `GOOGLE_CLIENT_ID`
   - `GOOGLE_CLIENT_SECRET`

   Inseriscili nel file `app.py`:
   ```python
   client_id="YOUR_GOOGLE_CLIENT_ID",
   client_secret="YOUR_GOOGLE_CLIENT_SECRET",
   ```

4. **Avvia il server Flask**
   ```bash
   python app.py
   ```

5. **Apri nel browser**
   ```
   http://127.0.0.1:5000
   ```

---

## 📁 File principali

| File/Cartella         | Descrizione                                  |
|-----------------------|----------------------------------------------|
| `app.py`              | Logica del server Flask e routing principale |
| `templates/`          | Pagine HTML (renderizzate da Flask)          |
| `static/`             | (opzionale) File CSS/JS personalizzati       |
| `README.md`           | Documentazione del progetto                   |
| `requirements.txt`    | Librerie Python necessarie                   |

---

## ✍️ Contribuire

Se vuoi contribuire:

1. Fai il fork del progetto
2. Crea una nuova branch (`git checkout -b feat-nuova-funzionalita`)
3. Fai il commit delle modifiche (`git commit -am 'Aggiunta nuova funzionalità'`)
4. Push sul tuo fork (`git push origin feat-nuova-funzionalita`)
5. Apri una Pull Request 🚀

---

## 📄 Licenza

Questo progetto è open-source e rilasciato sotto licenza **MIT**.

---

## 🙏 Ringraziamenti

Grazie a tutti i frequentatori di palestra che vivono i propri progressi come un gioco: **Ego Rank** è per voi.

---

## ✨ Descrizione breve per GitHub

> Una web app per chi va in palestra, con ranking gamificato delle alzate (bench, squat, deadlift), previsioni di avanzamento e accesso con Google o account personale. 💪
