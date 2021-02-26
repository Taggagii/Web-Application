drop table if exists weather;
    create table weather (
    id integer primary key autoincrement,
    city text not null,
    country text not null,
    lat decimal(6, 3) not null,
    lon decimal(6, 3) not null,
    last_call datetime,
    temperature integer not null,
    condition text not null,
    warnings text,
    precipitation integer not null,
    high integer not null,
    low integer not null
    );