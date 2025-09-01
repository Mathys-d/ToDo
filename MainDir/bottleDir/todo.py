import mysql.connector
from bottle import Bottle, request, template, static_file, redirect
from pathlib import Path

app = Bottle()
ABSOLUTE_APPLICATION_PATH = Path(__file__).parent



@app.get('/todo')
def todo_list():
    show  = request.query.show or 'open'
    match show:
        case 'open':
            db_query = "SELECT id, task FROM todo WHERE status = 1"
        case 'closed':
            db_query = "SELECT id, task FROM todo WHERE status = 0"
        case 'all':
            db_query = "SELECT id, task FROM todo"
        case _:
            return template('message.tpl',
                message = 'Wrong query parameter: show must be either open, closed or all.')

    connection = mysql.connector.connect(
        host="localhost",
        user="root",          # ton utilisateur MySQL
        password="1234",  # ton mot de passe MySQL
        database="todo"       # la base MySQL (à créer avant)
    )
    cursor = connection.cursor()
    cursor.execute(db_query)
    result = cursor.fetchall()
    connection.close()

    output = template('show_tasks.tpl', rows=result)
    return output



@app.route('/new', method=['GET', 'POST'])
def new_task():
    if request.POST:
        new_task = request.forms.task.strip()
        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # ton utilisateur MySQL
            password="1234",  # ton mot de passe MySQL
            database="todo"       # la base MySQL
        )
        cursor = connection.cursor()
        cursor.execute("INSERT INTO todo (task, status) VALUES (%s, %s)", (new_task, 1))
        connection.commit()
        new_id = cursor.lastrowid
        connection.close()

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

        connection = mysql.connector.connect(
            host="localhost",
            user="root",          # ton utilisateur MySQL
            password="1234",  # ton mot de passe MySQL
            database="todo"       # ta base MySQL
        )
        cursor = connection.cursor()
        cursor.execute(
            "UPDATE todo SET task = %s, status = %s WHERE id = %s",
            (new_data, status, number)
        )
        connection.commit()
        connection.close()

        return template('message.tpl',
            message=f'The task number {number} was successfully updated')
    else:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="todo"
        )
        cursor = connection.cursor()
        cursor.execute("SELECT task FROM todo WHERE id = %s", (number,))
        current_data = cursor.fetchone()
        connection.close()

        return template('edit_task', current_data=current_data, number=number)



@app.route('/as_json/<number:re:[0-9]+>')
def task_as_json(number):
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="1234",
        database="todo"
    )
    cursor = connection.cursor()
    cursor.execute("SELECT id, task, status FROM todo WHERE id = %s", (number,))
    result = cursor.fetchone()
    connection.close()

    if not result:
        return {'task': 'This task ID number does not exist!'}
    else:
        return {'id': result[0], 'task': result[1], 'status': result[2]}



@app.route('/static/<filepath:path>')
def send_static_file(filepath):
    ROOT_PATH = ABSOLUTE_APPLICATION_PATH / 'static'
    return static_file(filepath,
                       root=ROOT_PATH)



@app.error(404)
def something_went_wrong(error):
    return f'{error}: There is something wrong!'

@app.route('/')
def index():
    redirect('/todo')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True, reloader=True,server='waitress')