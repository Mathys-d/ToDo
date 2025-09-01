import mysql.connector

# Connexion sans préciser de base pour pouvoir la créer
connection = mysql.connector.connect(
    host="localhost",
    user="root",          # ton user MySQL
    password="1234"   # ton mot de passe MySQL
)
cursor = connection.cursor()

# Création de la base si elle n'existe pas
cursor.execute("CREATE DATABASE IF NOT EXISTS todo")
cursor.close()
connection.close()

# Connexion sur la base "todo"
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="todo"
)
cursor = connection.cursor()

# Création de la table si elle n'existe pas
cursor.execute("""
CREATE TABLE IF NOT EXISTS todo (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task VARCHAR(100) NOT NULL,
    status BOOLEAN NOT NULL
)
""")

# Insertion des données
cursor.execute("INSERT INTO todo (task, status) VALUES (%s, %s)",
               ("Read the Python tutorial to get a good introduction into Python", 0))
cursor.execute("INSERT INTO todo (task, status) VALUES (%s, %s)",
               ("Visit the Python website", 1))
cursor.execute("INSERT INTO todo (task, status) VALUES (%s, %s)",
               ("Test various editors for and check the syntax highlighting", 1))
cursor.execute("INSERT INTO todo (task, status) VALUES (%s, %s)",
               ("Choose your favorite WSGI-Framework", 0))

# Sauvegarde
connection.commit()

# Vérification (lecture des données)
cursor.execute("SELECT * FROM todo")
for row in cursor.fetchall():
    print(row)

cursor.close()
connection.close()
