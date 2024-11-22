from flask import Flask, render_template, session, redirect, url_for, request, flash, jsonify
import json
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_aqui'

# Configuración de la base de datos
def get_db():
    db = sqlite3.connect('database.db')
    db.row_factory = sqlite3.Row
    return db

# Crear tabla de preguntas si no existe
def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_text TEXT NOT NULL,
                options TEXT NOT NULL,
                correct_answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        db.commit()

# Inicializar la base de datos
init_db()

# Simulación de base de datos
users_db = {
    'admin@example.com': {'password': 'admin123', 'role': 'admin', 'name': 'Admin User'},
    'user@example.com': {'password': 'user123', 'role': 'postulante', 'name': 'Normal User'}
}

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/seccion2')
def seccion2():
    if not session.get('user'):
        flash('Debe iniciar sesión para acceder a esta sección')
        return redirect(url_for('home'))
    
    db = get_db()
    questions = db.execute('SELECT * FROM questions').fetchall()
    # Convertir las opciones de JSON string a lista
    questions_list = []
    for q in questions:
        question_dict = dict(q)
        question_dict['options'] = json.loads(question_dict['options'])
        questions_list.append(question_dict)
    
    return render_template('seccion2.html', questions=questions_list)

@app.route('/admin/preguntas/save', methods=['POST'])
def save_question():
    if not session.get('user') or session['user']['role'] != 'admin':
        return jsonify({'error': 'No autorizado'}), 403
    
    question_data = request.json
    db = get_db()
    db.execute('''
        INSERT INTO questions (question_text, options, correct_answer)
        VALUES (?, ?, ?)
    ''', (
        question_data['question'],
        json.dumps(question_data['options']),
        question_data['correctAnswer']
    ))
    db.commit()
    return jsonify({'success': True})

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    if email in users_db and users_db[email]['password'] == password:
        session['user'] = {
            'email': email,
            'role': users_db[email]['role'],
            'name': users_db[email]['name']
        }
        return redirect(url_for('home'))
    else:
        flash('Credenciales inválidas')
        return redirect(url_for('home'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/admin/preguntas')
def admin_preguntas():
    if not session.get('user') or session['user']['role'] != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('home'))
    return render_template('admin_preguntas.html')

@app.route('/admin/usuarios')
def gestion_usuarios():
    if not session.get('user') or session['user']['role'] != 'admin':
        flash('Acceso no autorizado')
        return redirect(url_for('home'))
    return render_template('gestion_usuarios.html')

if __name__ == '__main__':
    app.run(debug=True)