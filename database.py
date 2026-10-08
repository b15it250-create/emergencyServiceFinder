import sqlite3
from pathlib import Path

DB_PATH = Path("data/resqnear.db")

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        address TEXT NOT NULL,
        area TEXT,
        phone TEXT,
        alternate_phone TEXT,
        lat REAL NOT NULL,
        lon REAL NOT NULL,
        open_24x7 INTEGER DEFAULT 0,
        verified INTEGER DEFAULT 0,
        source TEXT DEFAULT 'Local Directory'
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS helplines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        phone TEXT NOT NULL,
        description TEXT,
        country TEXT DEFAULT 'India'
    )""")

    conn.commit()

    if cur.execute("SELECT COUNT(*) FROM services").fetchone()[0] == 0:
        seed_demo_data(conn)

    conn.close()

def seed_demo_data(conn):
    cur = conn.cursor()

    services = [
        ("City Civil Hospital","Hospital","Main Medical Road","Central Area","0361-0000001","",26.1462,91.7368,1,1,"Demo Directory"),
        ("Emergency Care Hospital","Hospital","Station Road","Ward 1","0361-0000002","",26.1500,91.7305,1,1,"Demo Directory"),
        ("Central Police Station","Police","Police Station Road","Central Area","0361-0000010","",26.1437,91.7349,1,1,"Demo Directory"),
        ("North Police Outpost","Police","North Link Road","Ward 2","0361-0000011","",26.1520,91.7390,1,1,"Demo Directory"),
        ("District Fire & Emergency Station","Fire Station","Fire Station Road","Ward 3","0361-0000020","",26.1418,91.7402,1,1,"Demo Directory"),
        ("Rapid Ambulance Service","Ambulance","Medical Complex","Central Area","0361-0000030","",26.1454,91.7376,1,1,"Demo Directory"),
        ("Community Blood Bank","Blood Bank","Hospital Campus","Central Area","0361-0000040","",26.1467,91.7364,0,1,"Demo Directory"),
        ("Disaster Response Control Room","Disaster Response","District Office","Administrative Area","0361-0000050","",26.1440,91.7335,1,1,"Demo Directory"),
        ("Women Support Centre","Women Support","Community Centre","Ward 4","0361-0000060","",26.1484,91.7420,0,1,"Demo Directory")
    ]

    cur.executemany("""INSERT INTO services
        (name,category,address,area,phone,alternate_phone,lat,lon,open_24x7,verified,source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", services)

    helplines = [
        ("Emergency Response Support System","General Emergency","112","Integrated emergency response number in India.","India"),
        ("Fire Emergency","Fire","101","Traditional fire emergency number; availability may vary by region.","India"),
        ("Police Emergency","Police","100","Traditional police emergency number; 112 is the integrated emergency number.","India"),
        ("Childline","Child Support","1098","Emergency assistance for children.","India"),
        ("Women Helpline","Women Support","181","Women support helpline used in many Indian states; local availability can vary.","India")
    ]

    cur.executemany("""INSERT INTO helplines
        (name,category,phone,description,country)
        VALUES (?,?,?,?,?)""", helplines)

    conn.commit()
