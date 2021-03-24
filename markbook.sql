DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS classes;
    CREATE TABLE classes (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        code TEXT(6) NOT NULL,
        grade INTEGER NOT NULL,
        teacher TEXT NOT NULL
    );
    CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        dob DATETIME NOT NULL,
        grade INTEGER NOT NULL
    );