DROP TABLE IF EXISTS weather;
    CREATE TABLE weather (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    temperature INTEGER NOT NULL,
    unit CHAR NOT NULL,
    username TEXT
    );