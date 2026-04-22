Live Site: https://basketball-position-analytics.onrender.com/analytics 

An analytics web app being built with **Flask** and **SQLite** that uses historical NBA data to recommend positions and training plans. By analyzing patterns and performance in NBA, the program identifies where a player's physical attributes and skill sets align with professional players.

---



### Tech Stack
* **Backend:** Flask (Python)
* **Database:** SQLite3
* **Frontend:** HTML5, CSS, JavaScript
* **Data Source:** NBA Player Stats 

---

### The Problem & Solution
**The Challenge:** Most amateur players train without a clear understanding of their natural strengths and weaknesses and where they fit on the court.

**The  Solution:** Pipeline that digests NBA performance trends (Points, Rebounds, Assists, True Shooting %, etc.). The system uses these data points to calculate a "Similarity Score" between the user and professional player profiles, outputting a data-backed training roadmap based on successful NBA patterns.

--

### How to Launch
py -m venv .venv

.\.venv\Scripts\Activate.ps1

py -m pip install --upgrade pip
py -m pip install -r my_flask_app/requirements.txt

python init_db.py (this creates/updates basketball.db)

Start the web app from the root folder: python my_flask_app/app.py

If PowerShell blocks activation, run `.\.venv\Scripts\activate.bat` from Command Prompt instead.

Open http://127.0.0.1:5000/ in your browser

### Deploy on Render
1. Push the repo to GitHub.
2. Log in to Render and create a new Web Service from the GitHub repo.
3. Let Render use the `render.yaml` blueprint in the repo root.
4. The build command installs dependencies and rebuilds the SQLite database with `init_db.py`.
5. The start command runs `gunicorn my_flask_app.app:app`.
6. Render will create the `SECRET_KEY` environment variable automatically from the blueprint.
7. Deploy the service and open the generated Render URL.

If you deploy manually instead of using the blueprint, use:
- Build command: `python -m pip install -r requirements.txt && python init_db.py`
- Start command: `gunicorn --chdir . my_flask_app.app:app`
