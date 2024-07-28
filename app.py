from datetime import datetime
from flask import Flask, make_response, request, render_template, redirect, url_for
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('planning.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS planning(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            task TEXT NOT NULL,
            obs TEXT NULL, 
            completed INTEGER DEFAULT 0           
        )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect('planning.db')
    conn.row_factory = sqlite3.Row 
    return conn

def get_current_month_year():
    now = datetime.now()
    current_month = now.strftime('%m')
    current_year = now.strftime('%Y')
    now_date = current_year + "-" + current_month
    return now_date

@app.route('/')
def index():
    color_mode = request.cookies.get('color_mode', 'dark')

    filter_month_year = request.args.get('filter_month_year', None)

    conn = get_db_connection()
    cursor = conn.cursor()

    #por padrao, será filtrado as tarefas do mês atual
    if not filter_month_year:
        filter_month_year = get_current_month_year()

    if filter_month_year:
        year, month = filter_month_year.split('-')
        cursor.execute('SELECT * FROM planning WHERE strftime("%m", date) = ? and strftime("%Y", date) = ?', (month, year))
    else:
        cursor.execute('SELECT * FROM planning')
    tasks = cursor.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks, color_mode=color_mode)

@app.route('/add', methods=['GET'])
def show_add_task_form():
    color_mode = request.cookies.get('color_mode', 'dark')
    return render_template('add.html', color_mode=color_mode)

@app.route('/add', methods=['POST'])
def add_task():
    date = request.form.get('date')
    task = request.form.get('task')
    obs = request.form.get('obs')

    if not date:
        return 'Data não fornecida', 400
    if not task:
        return 'Tarefa não fornecida', 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO planning (date, task, obs) VALUES (?, ?, ?)', (date, task, obs))
    conn.commit()
    conn.close()

    return redirect(url_for('index'))

@app.route('/edit/<int:task_id>', methods=['GET','POST'])
def edit_task(task_id):
    color_mode = request.cookies.get('color_mode', 'dark')

    conn = get_db_connection()
    cursor = conn.cursor()

    if request.method == 'POST':
        new_date = request.form['date']
        new_task = request.form['task']
        new_obs = request.form['obs']
        cursor.execute('UPDATE planning SET date = ?, task = ?, obs = ? WHERE id = ?', (new_date, new_task, new_obs, task_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    cursor.execute('SELECT * FROM planning WHERE id = ?', (task_id,))
    task = cursor.fetchone()
    conn.close()
    return render_template('edit.html', task=task, color_mode=color_mode)

@app.route('/delete/<int:task_id>', methods=['POST'])
def delete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM planning WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

@app.route('/tasks/complete/<int:task_id>', methods=['POST'])
def complete_task(task_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM planning WHERE id = ?', (task_id,))
    current_status = cursor.fetchone()['completed']
    new_status = 0 if current_status else 1
    
    cursor.execute('UPDATE planning SET completed = ? WHERE id = ?', (new_status, task_id))
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))
    
@app.route('/toogle-mode')
def toggle_mode():
    current_mode = request.cookies.get('color_mode','dark')
    new_mode = 'white' if current_mode == 'dark' else 'dark'
    response = make_response(redirect(url_for('index')))
    response.set_cookie('color_mode', new_mode)
    return response

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

