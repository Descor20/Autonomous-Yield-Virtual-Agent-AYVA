import sqlite3
from .connection import set_connection, get_connection
from .initialisation import INIT

def init() -> sqlite3.Connection:
    "Base filesystem neuf, en mémoire : chaque cas de test part du même état."
    conn = sqlite3.connect(":memory:", check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE files (id INTEGER PRIMARY KEY AUTOINCREMENT, firstname TEXT, lastname TEXT, job TEXT, birthdate TEXT, email TEXT, language TEXT);
    """)
    conn.executemany("INSERT INTO files VALUES (?, ?, ?, ?, ?, ?, ?)", INIT)
    conn.commit()
    set_connection(conn)
    return conn

def list_id() -> list[dict]:
    "Récupère une copie instantanée de la table des identitée."
    conn = get_connection()
    return [dict(r) for r in conn.execute("SELECT * FROM files ORDER BY id")]


def replace_or_write(firstname: str, lastname: str, job: str = None, birthdate: str = None, email: str = None, language: str = None) :
    "Ecrit un utilisateur dans la base de donnée, cela peut être un remplacement."
    conn = get_connection()
    
    conn.execute(
        "INSERT INTO files (firstname, lastname, job, birthdate, email, language) VALUES (?, ?, ?, ?, ?, ?)",
        (firstname, lastname, job, birthdate, email, language),
    )
    conn.commit()