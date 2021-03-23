DROP TABLE IF EXISTS students;
    CREATE TABLE students (
        id INTEGER PRIMARY KEY,
        last_name TEXT NOT NULL,
        first_name TEXT NOT NULL,
        dob DATETIME NOT NULL,
        grade INTEGER NOT NULL
    )