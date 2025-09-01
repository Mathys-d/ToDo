from bottle import Bottle, request, template, static_file, redirect
from pathlib import Path
import sqlite3


connection = sqlite3.connect('todo.db') # Warning: This file is created in the current directory
cursor = connection.cursor()
cursor.execute("CREATE TABLE todo (id INTEGER PRIMARY KEY, task char(100) NOT NULL, status bool NOT NULL)")
cursor.execute("INSERT INTO todo (task,status) VALUES ('Read the Python tutorial to get a good introduction into Python',0)")
cursor.execute("INSERT INTO todo (task,status) VALUES ('Visit the Python website',1)")
cursor.execute("INSERT INTO todo (task,status) VALUES ('Test various editors for and check the syntax highlighting',1)")
cursor.execute("INSERT INTO todo (task,status) VALUES ('Choose your favorite WSGI-Framework',0)")
connection.commit()


app = Bottle()
ABSOLUTE_APPLICATION_PATH = Path(__file__).parent



@app.get('/todo')
def todo_list():
    show  = request.query.show or 'open'
    match show:
        case 'open':
            db_query = "SELECT id, task, status FROM todo WHERE status LIKE '1'"
        case 'closed':
            db_query = "SELECT id, task, status FROM todo WHERE status LIKE '0'"
        case 'all':
            db_query = "SELECT id, task, status FROM todo"
        case _:
            return template('message.tpl',
                message = 'Wrong query parameter: show must be either open, closed or all.')
    with sqlite3.connect('todo.db') as connection:
        cursor = connection.cursor()
        cursor.execute(db_query)
        result = cursor.fetchall()
    output = template('show_tasks.tpl', rows=result)
    return output


@app.route('/new', method=['GET', 'POST'])
def new_task():
    if request.POST:
        new_task = request.forms.task.strip()
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO todo (task,status) VALUES (?,?)", (new_task, 1))
            new_id = cursor.lastrowid
        return template('message.tpl',
            message=f'The new task was inserted into the database, the ID is {new_id}')
    else:
        return template('new_task.tpl')


@app.route('/edit/<number:int>', method=['GET', 'POST'])
def edit_task(number):
    if request.POST:
        new_data = request.forms.task.strip()
        status = request.forms.status.strip()
        if status == 'open':
            status = 1
        else:
            status = 0
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute("UPDATE todo SET task = ?, status = ? WHERE id LIKE ?", (new_data, status, number))
        return template('message.tpl',
            message=f'The task number {number} was successfully updated')
    else:
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT task FROM todo WHERE id LIKE ?", (number,))
            current_data = cursor.fetchone()
        return template('edit_task', current_data=current_data, number=number)


@app.route('/details/<task:re:[0-9]+>')
def show_item(task):
        with sqlite3.connect('todo.db') as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT task, status FROM todo WHERE id LIKE ?", (task,))
            result = cursor.fetchone()
        if not result:
            return template('message.tpl',
            message = f'The task number {item} does not exist!')
        else:
            return template('message.tpl',
            message = f'Task: {result[0]}, status: {result[1]}')


@app.route('/as_json/<number:re:[0-9]+>')
def task_as_json(number):
    with sqlite3.connect('todo.db') as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT id, task, status FROM todo WHERE id LIKE ?", (number,))
        result = cursor.fetchone()
    if not result:
        return {'task': 'This task IF number does not exist!'}
    else:
        return {'id': result[0], 'task': result[1], 'status': result[2]}


@app.route('/static/<filepath:path>')
def send_static_file(filepath):
    ROOT_PATH = ABSOLUTE_APPLICATION_PATH / 'static'
    return static_file(filepath, root= ROOT_PATH)


@app.error(404)
def mistake404(error):
    return 'Sorry, this page does not exist!'

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True, reloader=True,server='waitress')