import os
import sqlite3
import datetime
import pandas as pd
import numpy as np
import joblib
from flask import (
    Flask, render_template, request, jsonify, redirect, url_for, session, g
)
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'weather_predictor_secret_key_antigravity'
DATABASE = os.path.join(os.path.dirname(__file__), 'database.db')
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model', 'weather_model.pkl')

# Global ML Pipeline instance
ml_pipeline = None

def load_ml_model():
    global ml_pipeline
    if os.path.exists(MODEL_PATH):
        try:
            ml_pipeline = joblib.load(MODEL_PATH)
            print("Loaded ML model successfully.")
        except Exception as e:
            print(f"Error loading model: {e}")
            ml_pipeline = None
    else:
        print("ML model file not found. Running training...")
        from train_model import train_and_save_model
        ml_pipeline = train_and_save_model()

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create predictions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                temperature REAL NOT NULL,
                humidity REAL NOT NULL,
                wind_speed REAL NOT NULL,
                pressure REAL NOT NULL,
                uv_index REAL NOT NULL,
                rain_prob REAL NOT NULL,
                season TEXT NOT NULL,
                time_of_day TEXT NOT NULL,
                prediction TEXT NOT NULL,
                comfort_index INTEGER NOT NULL,
                suggestion TEXT NOT NULL,
                weather_icon TEXT NOT NULL,
                theme_color TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        db.commit()
        
        # Seed default Admin and Demo user
        cursor.execute("SELECT * FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', ('admin', 'admin@weatherfeel.ai', generate_password_hash('admin123'), 'admin'))
            
        cursor.execute("SELECT * FROM users WHERE username = 'demo'")
        demo_user = cursor.fetchone()
        if not demo_user:
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, role)
                VALUES (?, ?, ?, ?)
            ''', ('demo', 'demo@weatherfeel.ai', generate_password_hash('demo123'), 'user'))
            db.commit()
            cursor.execute("SELECT id FROM users WHERE username = 'demo'")
            demo_user = cursor.fetchone()
            
        demo_id = demo_user['id'] if demo_user else 1
        
        # Seed initial predictions for stats if empty
        cursor.execute("SELECT COUNT(*) as count FROM predictions")
        if cursor.fetchone()['count'] == 0:
            sample_data = [
                (demo_id, 25.0, 50.0, 15.0, 1013.0, 5.0, 10.0, 'Summer', 'Afternoon', 'Comfortable', 85, 'Wear light cotton T-shirt.', '☀️', '#32CD32'),
                (demo_id, 5.0, 70.0, 25.0, 1020.0, 2.0, 30.0, 'Winter', 'Morning', 'Very Cold', 25, 'Wear heavy jacket, gloves & warm cap.', '🥶', '#00BFFF'),
                (demo_id, 38.0, 85.0, 10.0, 1005.0, 9.0, 80.0, 'Summer', 'Afternoon', 'Very Hot', 15, 'Stay hydrated! Drink 3-4L water.', '🔥', '#FF4500'),
                (demo_id, 18.0, 60.0, 12.0, 1015.0, 4.0, 20.0, 'Spring', 'Morning', 'Cool', 75, 'Light sweater or jacket recommended.', '🌤️', '#90EE90'),
                (demo_id, -5.0, 80.0, 30.0, 1025.0, 1.0, 90.0, 'Winter', 'Night', 'Freezing', 10, 'Heavy winter gear essential. Stay indoors.', '🧊', '#00BFFF')
            ]
            cursor.executemany('''
                INSERT INTO predictions 
                (user_id, temperature, humidity, wind_speed, pressure, uv_index, rain_prob, season, time_of_day, prediction, comfort_index, suggestion, weather_icon, theme_color)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', sample_data)
            db.commit()

# Comfort % & Suggestion Logic Helper
def calculate_comfort_and_suggestion(temp, humidity, wind_speed, pressure, uv_index, rain_prob):
    # Base comfort calculation (ideal temp around 22°C, low wind, moderate humidity)
    temp_penalty = abs(temp - 22) * 2.2
    humidity_penalty = abs(humidity - 45) * 0.4
    wind_penalty = max(0, wind_speed - 20) * 0.5
    uv_penalty = max(0, uv_index - 6) * 3
    rain_penalty = rain_prob * 0.2
    
    raw_comfort = 100 - (temp_penalty + humidity_penalty + wind_penalty + uv_penalty + rain_penalty)
    comfort_index = int(max(5, min(98, raw_comfort)))
    
    # Suggestions & icon
    if temp < 0:
        suggestion = "Heavy winter coat, thermal layers, gloves & scarf required."
        icon = "🧊"
        color = "#00BFFF" # Blue
        effect = "snow"
    elif temp < 15:
        if rain_prob > 50 or humidity > 80:
            suggestion = "Chilly & damp. Wear a waterproof warm jacket."
            icon = "🌧️"
            effect = "rain"
        else:
            suggestion = "Cold weather. Wear a jacket or cozy wool sweater."
            icon = "❄️"
            effect = "clouds"
        color = "#38bdf8"
    elif temp <= 30:
        if rain_prob > 60:
            suggestion = "Pleasant temperature, but rain is expected. Carry an umbrella."
            icon = "🌦️"
            effect = "rain"
            color = "#a855f7"
        else:
            suggestion = "Optimal weather! Comfortable cotton clothes are recommended."
            icon = "🌤️"
            effect = "sunny"
            color = "#34d399" # Green
    elif temp <= 38:
        suggestion = "Warm to Hot. Drink plenty of water (2.5-3L) and wear light clothes."
        icon = "☀️"
        effect = "sunny"
        color = "#fbbf24" # Orange
    else:
        suggestion = "Extreme heat alert! Stay indoors during peak hours and stay hydrated."
        icon = "🔥"
        effect = "heatwave"
        color = "#f87171" # Red
        
    return comfort_index, suggestion, icon, color, effect

# Authentication Helper
def get_current_user():
    if 'user_id' in session:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, username, email, role FROM users WHERE id = ?", (session['user_id'],))
        return cursor.fetchone()
    return None

# -----------------------------
# Web Page Routes
# -----------------------------
@app.route('/')
def index():
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html', user=user)

@app.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/predict')
def predict_page():
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))
    return render_template('predict.html', user=user)

@app.route('/history')
def history_page():
    user = get_current_user()
    if not user:
        return redirect(url_for('login_page'))
    return render_template('history.html', user=user)

@app.route('/admin')
def admin_page():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return redirect(url_for('index'))
    return render_template('admin.html', user=user)

# -----------------------------
# Authentication API
# -----------------------------
@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json() or request.form
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? OR email = ?", (username, username))
    user = cursor.fetchone()
    
    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['username'] = user['username']
        session['role'] = user['role']
        return jsonify({'success': True, 'message': 'Login successful!', 'role': user['role']})
    
    return jsonify({'success': False, 'message': 'Invalid username or password.'}), 401

@app.route('/api/register', methods=['POST'])
def api_register():
    data = request.get_json() or request.form
    username = data.get('username', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()
    
    if not username or not email or not password:
        return jsonify({'success': False, 'message': 'All fields are required.'}), 400
        
    db = get_db()
    cursor = db.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, 'user')
        ''', (username, email, generate_password_hash(password)))
        db.commit()
        
        # Log user in
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        session['user_id'] = user['id']
        session['username'] = username
        session['role'] = 'user'
        
        return jsonify({'success': True, 'message': 'Registration successful!'})
    except sqlite3.IntegrityError:
        return jsonify({'success': False, 'message': 'Username or Email already exists.'}), 400

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_page'))

# -----------------------------
# Prediction REST API
# -----------------------------
@app.route('/api/predict', methods=['POST'])
def api_predict():
    data = request.get_json() or {}
    
    try:
        temp = float(data.get('temperature', 25))
        humidity = float(data.get('humidity', 50))
        wind_speed = float(data.get('wind_speed', 15))
        pressure = float(data.get('pressure', 1013))
        uv_index = float(data.get('uv_index', 5))
        rain_prob = float(data.get('rain_prob', 10))
        season = data.get('season', 'Summer')
        time_of_day = data.get('time_of_day', 'Afternoon')
    except (ValueError, TypeError):
        return jsonify({'success': False, 'message': 'Invalid numeric parameters.'}), 400
        
    input_df = pd.DataFrame([{
        'temperature': temp,
        'humidity': humidity,
        'wind_speed': wind_speed,
        'pressure': pressure,
        'uv_index': uv_index,
        'rain_prob': rain_prob,
        'season': season,
        'time_of_day': time_of_day
    }])
    
    global ml_pipeline
    if ml_pipeline is None:
        load_ml_model()
        
    if ml_pipeline:
        prediction = ml_pipeline.predict(input_df)[0]
    else:
        # Fallback prediction
        if temp < 0: feel = "Freezing"
        elif temp < 15: feel = "Cold"
        elif temp < 25: feel = "Pleasant"
        elif temp < 35: feel = "Warm"
        else: feel = "Hot"
        prediction = feel
        
    comfort_index, suggestion, icon, theme_color, effect = calculate_comfort_and_suggestion(
        temp, humidity, wind_speed, pressure, uv_index, rain_prob
    )
    
    # Save to history if logged in
    user_id = session.get('user_id')
    if user_id:
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO predictions 
            (user_id, temperature, humidity, wind_speed, pressure, uv_index, rain_prob, season, time_of_day, prediction, comfort_index, suggestion, weather_icon, theme_color)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, temp, humidity, wind_speed, pressure, uv_index, rain_prob, season, time_of_day, prediction, comfort_index, suggestion, icon, theme_color))
        db.commit()
        
    return jsonify({
        'success': True,
        'prediction': prediction,
        'comfort_index': comfort_index,
        'suggestion': suggestion,
        'weather_icon': icon,
        'theme_color': theme_color,
        'effect': effect,
        'temperature': temp
    })

# -----------------------------
# History & Stats REST API
# -----------------------------
@app.route('/api/history', methods=['GET'])
def api_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    search = request.args.get('search', '').strip()
    db = get_db()
    cursor = db.cursor()
    
    if search:
        query = '''
            SELECT * FROM predictions 
            WHERE user_id = ? AND (prediction LIKE ? OR suggestion LIKE ? OR season LIKE ?)
            ORDER BY created_at DESC
        '''
        term = f"%{search}%"
        cursor.execute(query, (user_id, term, term, term))
    else:
        cursor.execute('SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
        
    rows = cursor.fetchall()
    history = [dict(row) for row in rows]
    return jsonify({'success': True, 'history': history})

@app.route('/api/history/<int:pred_id>', methods=['DELETE'])
def api_delete_history(pred_id):
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM predictions WHERE id = ? AND user_id = ?', (pred_id, user_id))
    db.commit()
    return jsonify({'success': True, 'message': 'Entry deleted.'})

@app.route('/api/history/clear', methods=['POST'])
def api_clear_history():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM predictions WHERE user_id = ?', (user_id,))
    db.commit()
    return jsonify({'success': True, 'message': 'All history cleared.'})

@app.route('/api/stats', methods=['GET'])
def api_stats():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
        
    db = get_db()
    cursor = db.cursor()
    
    # Total count
    cursor.execute('SELECT COUNT(*) as total FROM predictions WHERE user_id = ?', (user_id,))
    total = cursor.fetchone()['total']
    
    # Avg Temp & Comfort
    cursor.execute('SELECT AVG(temperature) as avg_temp, AVG(comfort_index) as avg_comfort FROM predictions WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    avg_temp = round(row['avg_temp'], 1) if row['avg_temp'] else 0.0
    avg_comfort = round(row['avg_comfort'], 1) if row['avg_comfort'] else 0.0
    
    # Recent predictions
    cursor.execute('SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT 5', (user_id,))
    recent = [dict(r) for r in cursor.fetchall()]
    
    # Frequency by prediction category
    cursor.execute('SELECT prediction, COUNT(*) as cnt FROM predictions WHERE user_id = ? GROUP BY prediction', (user_id,))
    freq_data = {r['prediction']: r['cnt'] for r in cursor.fetchall()}
    
    # Temperature history (last 10)
    cursor.execute('SELECT temperature, comfort_index, created_at FROM predictions WHERE user_id = ? ORDER BY created_at ASC LIMIT 10', (user_id,))
    trend_rows = cursor.fetchall()
    temps = [r['temperature'] for r in trend_rows]
    comforts = [r['comfort_index'] for r in trend_rows]
    labels = [r['created_at'][11:16] if len(r['created_at']) >= 16 else r['created_at'] for r in trend_rows]
    
    return jsonify({
        'success': True,
        'total_predictions': total,
        'avg_temperature': avg_temp,
        'avg_comfort': avg_comfort,
        'recent_predictions': recent,
        'freq_data': freq_data,
        'trend': {
            'labels': labels,
            'temperatures': temps,
            'comforts': comforts
        }
    })

# -----------------------------
# Admin REST APIs
# -----------------------------
@app.route('/api/admin/users', methods=['GET'])
def api_admin_users():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, username, email, role, created_at FROM users')
    users = [dict(r) for r in cursor.fetchall()]
    return jsonify({'success': True, 'users': users})

@app.route('/api/admin/users/<int:uid>', methods=['DELETE'])
def api_admin_delete_user(uid):
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    if uid == user['id']:
        return jsonify({'success': False, 'message': 'Cannot delete logged in admin account.'}), 400
        
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM predictions WHERE user_id = ?', (uid,))
    cursor.execute('DELETE FROM users WHERE id = ?', (uid,))
    db.commit()
    return jsonify({'success': True, 'message': 'User deleted successfully.'})

@app.route('/api/admin/retrain', methods=['POST'])
def api_admin_retrain():
    user = get_current_user()
    if not user or user['role'] != 'admin':
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        from train_model import train_and_save_model
        global ml_pipeline
        ml_pipeline = train_and_save_model()
        return jsonify({'success': True, 'message': 'AI Model retrained and updated successfully!'})
    except Exception as e:
        return jsonify({'success': False, 'message': f'Retraining failed: {str(e)}'}), 500

if __name__ == '__main__':
    load_ml_model()
    init_db()
    print("Starting WeatherPredictor Flask Server on http://localhost:5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
