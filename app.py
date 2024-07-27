from flask import Flask, request, render_template, redirect, url_for
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

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM planning')
    tasks = cursor.fetchall()
    conn.close()
    return render_template('index.html', tasks=tasks)

@app.route('/add', methods=['GET'])
def show_add_task_form():
    return render_template('add.html')

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
    return render_template('edit.html', task=task)

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
    

if __name__ == "__main__":
    init_db()
    app.run(debug=True)

