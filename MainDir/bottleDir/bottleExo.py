import mysql.connector
from bottle import Bottle


app = Bottle()

@app.route('/todo')
def todo_list():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",          # ton utilisateur MySQL
        password="1234",  # ton mot de passe MySQL
        database="todo"       # la base que tu as créée avant
    )
    cursor = connection.cursor()
    cursor.execute("SELECT id, task, status FROM todo WHERE status = 1")
    result = cursor.fetchall()
    connection.close()
    return str(result)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
