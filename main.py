# main.py
from fastapi import FastAPI, Request, Form, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
from itsdangerous import URLSafeSerializer
import secrets
import sqlite3
import json
from datetime import datetime
import bcrypt

from questions import PROFILES, PROFILE_DETAILS
from api_client import fetch_quote

app = FastAPI(title="Psy Quiz")

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

SECRET_KEY = secrets.token_urlsafe(32)
serializer = URLSafeSerializer(SECRET_KEY)

DB_FILE = "psyquiz.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_psychologist BOOLEAN DEFAULT 0,
            created_at TEXT NOT NULL
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            answers TEXT NOT NULL,
            dominant_profile TEXT NOT NULL,
            scores TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            choices TEXT NOT NULL,
            order_index INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def migrate_questions():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM questions")
    count = c.fetchone()[0]
    if count == 0:
        from questions import QUESTIONS
        for idx, q in enumerate(QUESTIONS):
            choices_json = json.dumps(q["choices"])
            c.execute('''
                INSERT INTO questions (text, choices, order_index)
                VALUES (?, ?, ?)
            ''', (q["text"], choices_json, idx))
        conn.commit()
    conn.close()

migrate_questions()

def get_all_questions():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, text, choices, order_index FROM questions ORDER BY order_index')
    rows = c.fetchall()
    conn.close()
    questions = []
    for row in rows:
        questions.append({
            "id": row[0],
            "text": row[1],
            "choices": json.loads(row[2]),
            "order_index": row[3]
        })
    return questions

def get_question_by_id(qid: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, text, choices, order_index FROM questions WHERE id = ?', (qid,))
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "id": row[0],
            "text": row[1],
            "choices": json.loads(row[2]),
            "order_index": row[3]
        }
    return None

def update_question(qid: int, text: str, choices: list, order_index: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    choices_json = json.dumps(choices)
    c.execute('''
        UPDATE questions SET text = ?, choices = ?, order_index = ? WHERE id = ?
    ''', (text, choices_json, order_index, qid))
    conn.commit()
    conn.close()

def delete_question(qid: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM questions WHERE id = ?', (qid,))
    conn.commit()
    conn.close()

def create_question(text: str, choices: list, order_index: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    choices_json = json.dumps(choices)
    c.execute('''
        INSERT INTO questions (text, choices, order_index) VALUES (?, ?, ?)
    ''', (text, choices_json, order_index))
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return new_id

def hash_password(password: str) -> str:
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    try:
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except:
        return False

def get_user_by_username(username: str) -> Optional[dict]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, username, password_hash, is_psychologist FROM users WHERE username = ?', (username,))
    row = c.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "password_hash": row[2], "is_psychologist": row[3]}
    return None

def create_user(username: str, password: str, is_psychologist: bool = False) -> Optional[int]:
    password_hash = hash_password(password)
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    try:
        c.execute('''
            INSERT INTO users (username, password_hash, is_psychologist, created_at)
            VALUES (?, ?, ?, ?)
        ''', (username, password_hash, is_psychologist, datetime.now().isoformat()))
        conn.commit()
        user_id = c.lastrowid
    except sqlite3.IntegrityError:
        user_id = None
    finally:
        conn.close()
    return user_id

def save_result(user_id: int, answers: List[int], dominant_profile: str, scores_dict: dict):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    answers_json = json.dumps(answers)
    scores_json = json.dumps(scores_dict)
    date_str = datetime.now().isoformat()
    c.execute('''
        INSERT INTO results (user_id, date, answers, dominant_profile, scores)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, date_str, answers_json, dominant_profile, scores_json))
    conn.commit()
    conn.close()

def get_results_by_user_id(user_id: int) -> List[dict]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT date, dominant_profile, scores FROM results
        WHERE user_id = ? ORDER BY date DESC
    ''', (user_id,))
    rows = c.fetchall()
    conn.close()
    history = []
    for date, profile, scores_json in rows:
        scores = json.loads(scores_json)
        history.append({
            "date": date[:10],
            "profile": profile,
            "scores": scores
        })
    return history

def get_all_users_with_results() -> List[dict]:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('SELECT id, username, created_at FROM users WHERE is_psychologist = 0 ORDER BY username')
    users = c.fetchall()
    result = []
    for user_id, username, created_at in users:
        c.execute('''
            SELECT date, dominant_profile, scores FROM results
            WHERE user_id = ? ORDER BY date DESC
        ''', (user_id,))
        rows = c.fetchall()
        results_list = []
        for date, profile, scores_json in rows:
            scores = json.loads(scores_json)
            results_list.append({
                "date": date[:10],
                "profile": profile,
                "scores": scores
            })
        result.append({
            "user_id": user_id,
            "username": username,
            "created_at": created_at[:10],
            "results": results_list
        })
    conn.close()
    return result

def delete_user(user_id: int):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('DELETE FROM results WHERE user_id = ?', (user_id,))
    c.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

def get_username_from_cookie(request: Request) -> Optional[str]:
    session_cookie = request.cookies.get("session")
    if session_cookie:
        try:
            data = serializer.loads(session_cookie)
            return data.get("username")
        except:
            return None
    return None

def get_user_id_from_cookie(request: Request) -> Optional[int]:
    session_cookie = request.cookies.get("session")
    if session_cookie:
        try:
            data = serializer.loads(session_cookie)
            return data.get("user_id")
        except:
            return None
    return None

def compute_scores(answers: List[int]) -> List[int]:
    scores = [0] * 10
    questions = get_all_questions()
    for i, choice_idx in enumerate(answers):
        if i < len(questions) and choice_idx < len(questions[i]["choices"]):
            choice_scores = questions[i]["choices"][choice_idx]["scores"]
            for j in range(10):
                scores[j] += choice_scores[j]
    return scores

def get_dominant_profile(scores: List[int]) -> int:
    return scores.index(max(scores))

# ====================== Routes publiques ======================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    username = get_username_from_cookie(request)
    if username:
        user = get_user_by_username(username)
        if user and user.get("is_psychologist"):
            return RedirectResponse(url="/admin/dashboard", status_code=302)
        else:
            return RedirectResponse(url="/question/0", status_code=302)
    response = templates.TemplateResponse("home.html", {"request": request})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.get("/login-patient", response_class=HTMLResponse)
async def login_patient_page(request: Request):
    response = templates.TemplateResponse("login_patient.html", {"request": request})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.post("/login-patient")
async def login_patient(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]) or user.get("is_psychologist"):
        return templates.TemplateResponse("login_patient.html", {"request": request, "error": "Identifiants incorrects ou compte non autorisé."})
    session_data = serializer.dumps({"user_id": user["id"], "username": user["username"], "answers": {}})
    response = RedirectResponse(url="/question/0", status_code=302)
    response.set_cookie(key="session", value=session_data, httponly=True, max_age=3600*24)
    return response

@app.get("/login-admin", response_class=HTMLResponse)
async def login_admin_page(request: Request):
    response = templates.TemplateResponse("login_admin.html", {"request": request})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.post("/login-admin")
async def login_admin(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    user = get_user_by_username(username)
    if not user or not verify_password(password, user["password_hash"]) or not user.get("is_psychologist"):
        return templates.TemplateResponse("login_admin.html", {"request": request, "error": "Identifiants incorrects ou compte non autorisé."})
    session_data = serializer.dumps({"user_id": user["id"], "username": user["username"], "answers": {}})
    response = RedirectResponse(url="/admin/dashboard", status_code=302)
    response.set_cookie(key="session", value=session_data, httponly=True, max_age=3600*24)
    return response

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    response = templates.TemplateResponse("register.html", {"request": request})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.post("/register")
async def register(request: Request, response: Response, username: str = Form(...), password: str = Form(...)):
    if not username.strip() or not password.strip():
        return templates.TemplateResponse("register.html", {"request": request, "error": "Veuillez remplir tous les champs."})
    if len(password.encode('utf-8')) > 72:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Le mot de passe ne doit pas dépasser 72 caractères."})
    user_id = create_user(username.strip(), password)
    if user_id is None:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Ce nom d'utilisateur est déjà pris."})
    session_data = serializer.dumps({"user_id": user_id, "username": username.strip(), "answers": {}})
    response = RedirectResponse(url="/question/0", status_code=302)
    response.set_cookie(key="session", value=session_data, httponly=True, max_age=3600*24)
    return response

@app.get("/logout")
async def logout(response: Response):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("session")
    return response

@app.get("/question/{q_index}", response_class=HTMLResponse)
async def show_question(request: Request, q_index: int):
    username = get_username_from_cookie(request)
    if not username:
        return RedirectResponse(url="/login-patient", status_code=302)
    questions = get_all_questions()
    if q_index < 0 or q_index >= len(questions):
        raise HTTPException(status_code=404, detail="Question non trouvée")
    user = get_user_by_username(username)
    is_psychologist = user.get("is_psychologist", False) if user else False
    session_cookie = request.cookies.get("session")
    answers_dict = {}
    if session_cookie:
        try:
            data = serializer.loads(session_cookie)
            answers_dict = data.get("answers", {})
        except:
            pass
    question = questions[q_index]
    total = len(questions)
    response = templates.TemplateResponse(
        "question.html",
        {
            "request": request,
            "username": username,
            "is_psychologist": is_psychologist,
            "question": question,
            "q_index": q_index,
            "total": total,
            "selected": answers_dict.get(str(q_index)),
            "prev_index": q_index - 1 if q_index > 0 else None,
            "next_index": q_index + 1 if q_index < total - 1 else None,
        }
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.post("/question/{q_index}")
async def submit_question(
    request: Request,
    response: Response,
    q_index: int,
    answer: int = Form(...),
    action: str = Form(...)
):
    username = get_username_from_cookie(request)
    if not username:
        return RedirectResponse(url="/login-patient", status_code=302)
    questions = get_all_questions()
    if q_index < 0 or q_index >= len(questions):
        raise HTTPException(status_code=404)
    session_cookie = request.cookies.get("session")
    session_data = {}
    if session_cookie:
        try:
            session_data = serializer.loads(session_cookie)
        except:
            pass
    answers = session_data.get("answers", {})
    answers[str(q_index)] = answer
    session_data["answers"] = answers
    new_session_data = serializer.dumps(session_data)
    if action == "next":
        if q_index == len(questions) - 1:
            redirect_url = "/result"
        else:
            redirect_url = f"/question/{q_index + 1}"
    elif action == "prev":
        if q_index > 0:
            redirect_url = f"/question/{q_index - 1}"
        else:
            redirect_url = "/question/0"
    else:
        redirect_url = f"/question/{q_index}"
    response = RedirectResponse(url=redirect_url, status_code=302)
    response.set_cookie(key="session", value=new_session_data, httponly=True, max_age=3600*24)
    return response

@app.get("/result", response_class=HTMLResponse)
async def result(request: Request):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-patient", status_code=302)
    session_cookie = request.cookies.get("session")
    answers_dict = {}
    if session_cookie:
        try:
            data = serializer.loads(session_cookie)
            answers_dict = data.get("answers", {})
        except:
            pass
    questions = get_all_questions()
    answers = []
    for i in range(len(questions)):
        if str(i) in answers_dict:
            answers.append(answers_dict[str(i)])
        else:
            return RedirectResponse(url=f"/question/{i}", status_code=302)
    scores = compute_scores(answers)
    dominant_idx = get_dominant_profile(scores)
    dominant_profile = PROFILES[dominant_idx]
    details = PROFILE_DETAILS[dominant_idx]
    quote = await fetch_quote()
    scores_dict = {PROFILES[i]: scores[i] for i in range(10)}
    save_result(user_id, answers, dominant_profile, scores_dict)
    session_data = {"user_id": user_id, "username": username, "answers": {}}
    new_session_data = serializer.dumps(session_data)
    user = get_user_by_username(username)
    is_psychologist = user.get("is_psychologist", False) if user else False

    context = {
        "request": request,
        "username": username,
        "dominant_profile": dominant_profile,
        "description": details["description"],
        "advice": details["advice"],
        "traits": details["traits"],
        "exploration": details.get("exploration", []),
        "questions": details.get("questions", []),
        "work": details.get("work", []),
        "themes": details.get("themes", []),
        "quote": quote["content"],
        "author": quote["author"],
        "scores": scores_dict,
        "is_psychologist": is_psychologist
    }
    response = templates.TemplateResponse("result.html", context)
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.set_cookie(key="session", value=new_session_data, httponly=True, max_age=3600*24)
    return response

@app.get("/history", response_class=HTMLResponse)
async def history(request: Request):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-patient", status_code=302)
    history_list = get_results_by_user_id(user_id)
    response = templates.TemplateResponse(
        "history.html",
        {"request": request, "username": username, "history": history_list}
    )
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

# ====================== Routes d'administration ======================

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    response = templates.TemplateResponse("admin_dashboard.html", {"request": request, "username": username})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.get("/admin/questions", response_class=HTMLResponse)
async def admin_questions(request: Request):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    questions = get_all_questions()
    response = templates.TemplateResponse("admin_questions.html", {"request": request, "username": username, "questions": questions})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.get("/admin/questions/add", response_class=HTMLResponse)
async def admin_add_question_form(request: Request):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    response = templates.TemplateResponse("admin_question_form.html", {"request": request, "username": username, "question": None})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.post("/admin/questions/add")
async def admin_add_question(request: Request, response: Response, text: str = Form(...), choices_json: str = Form(...)):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    try:
        choices = json.loads(choices_json)
        if not isinstance(choices, list) or len(choices) < 1:
            raise ValueError
    except:
        return templates.TemplateResponse("admin_question_form.html", {"request": request, "username": username, "error": "Format JSON invalide pour les choix"})
    questions = get_all_questions()
    new_order = len(questions)
    create_question(text, choices, new_order)
    return RedirectResponse(url="/admin/questions", status_code=302)

@app.get("/admin/questions/edit/{qid}", response_class=HTMLResponse)
async def admin_edit_question_form(request: Request, qid: int):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    question = get_question_by_id(qid)
    if not question:
        raise HTTPException(status_code=404)
    response = templates.TemplateResponse("admin_question_form.html", {"request": request, "username": username, "question": question})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.post("/admin/questions/edit/{qid}")
async def admin_edit_question(request: Request, qid: int, text: str = Form(...), choices_json: str = Form(...), order_index: int = Form(...)):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    try:
        choices = json.loads(choices_json)
        if not isinstance(choices, list) or len(choices) < 1:
            raise ValueError
    except:
        question = get_question_by_id(qid)
        return templates.TemplateResponse("admin_question_form.html", {"request": request, "username": username, "question": question, "error": "Format JSON invalide pour les choix"})
    update_question(qid, text, choices, order_index)
    return RedirectResponse(url="/admin/questions", status_code=302)

@app.get("/admin/questions/delete/{qid}")
async def admin_delete_question(request: Request, qid: int):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    delete_question(qid)
    return RedirectResponse(url="/admin/questions", status_code=302)

@app.get("/admin/patients", response_class=HTMLResponse)
async def admin_patients(request: Request):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    patients = get_all_users_with_results()
    response = templates.TemplateResponse("admin_patients.html", {"request": request, "username": username, "patients": patients})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return response

@app.get("/admin/patients/delete/{pid}")
async def admin_delete_patient(request: Request, pid: int):
    user_id = get_user_id_from_cookie(request)
    username = get_username_from_cookie(request)
    if not user_id or not username:
        return RedirectResponse(url="/login-admin", status_code=302)
    user = get_user_by_username(username)
    if not user or not user.get("is_psychologist"):
        return RedirectResponse(url="/", status_code=302)
    delete_user(pid)
    return RedirectResponse(url="/admin/patients", status_code=302)

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    try:
        return FileResponse('static/favicon.ico')
    except:
        return Response(status_code=204)

def create_default_psychologist():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if not c.fetchone():
        password_hash = hash_password("admin")
        c.execute('''
            INSERT INTO users (username, password_hash, is_psychologist, created_at)
            VALUES (?, ?, ?, ?)
        ''', ("admin", password_hash, 1, datetime.now().isoformat()))
        conn.commit()
    conn.close()

create_default_psychologist()