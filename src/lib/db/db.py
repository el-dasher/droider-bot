from os.path import isfile
from sqlite3 import connect

DB_PATH = "./data/db/database.db"
BUILD_PATH = "./data/db/build.sql"

connection = connect(DB_PATH)
cursor = connection.cursor()


def commit():
    connection.commit()


def close():
    connection.close()


def with_commit(func):
    def inner(*args, **kwargs):
        func(*args, **kwargs)
        commit()

    return inner


def scriptexec(path):
    with open(path, "r", encoding="utf-8") as script:
        cursor.execute(script.read())


@with_commit
def build_db():
    if isfile(DB_PATH):
        scriptexec(BUILD_PATH)


def execute(command, *values):
    cursor.execute(command, tuple(*values))


def field(command, *values):
    execute(command, *values)

    if fetch := cursor.fetchone() is not None:
        return fetch[0]


def record(command, *values):
    execute(command, *values)

    return cursor.fetchone()


def records(command, *values):
    execute(command, *values)

    return cursor.fetchall()


def column(command, *values):
    execute(command, *values)

    return [item[0] for item in cursor.fetchall()]


def multiexec(command, valueset):
    cursor.executemany(command, valueset)

