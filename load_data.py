"""Part 1: Data Management

Using the data provided in cell-count.csv, your first task is to:

Design a relational database schema (using SQLite) that models this data effectively.

Create a Python script named "load_data.py" in the root directory of your repository that:

Initializes the database with your schema.

Loads all rows from cell-count.csv.

Requirements:
The script must be named `load_data.py` and located in the root directory (not in subdirectories like `src/`).
 - When executed with `python load_data.py`, it should create a SQLite database file (`.db` extension) in the repository root.
- The script should be executable directly without command-line arguments or module-style execution (`python -m`).
"""

import sqlite3
import csv

#setting up the table
connection = sqlite3.connect("database.db")
cursor = connection.cursor()
cursor.executescript('''
    CREATE TABLE IF NOT EXISTS projects (
            project_id   TEXT PRIMARY KEY
        );
                
    CREATE TABLE IF NOT EXISTS subjects (
            subject_id   TEXT PRIMARY KEY,
            project_id   TEXT NOT NULL,
            condition    TEXT,
            age          INTEGER,
            sex          TEXT,
            treatment    TEXT,
            response     TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        );

    CREATE TABLE IF NOT EXISTS samples (
            sample_id                  TEXT PRIMARY KEY,
            subject_id                 TEXT NOT NULL,
            project_id                 TEXT NOT NULL,
            sample_type                TEXT,
            time_from_treatment_start  INTEGER,
            FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
            FOREIGN KEY (project_id) REFERENCES projects(project_id)
        );
 
    CREATE TABLE IF NOT EXISTS cell_counts (
            sample_id   TEXT PRIMARY KEY,
            b_cell      INTEGER,
            cd8_t_cell  INTEGER,
            cd4_t_cell  INTEGER,
            nk_cell     INTEGER,
            monocyte    INTEGER,
            FOREIGN KEY (sample_id) REFERENCES samples(sample_id)                   
''')

#now to load the csv
with open("cell-count.csv", newline="") as csvfile:
    reader = csv.DictReader(csvfile)

    for row in reader:
        # insert into projects
        cursor.execute("""
            INSERT OR IGNORE INTO projects (project_id)
            VALUES (?)
        """, (row["project_id"],))

        # insert into subjects
        cursor.execute("""
            INSERT OR IGNORE INTO subjects (
                subject_id, project_id, condition, age, sex, treatment, response
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            row["subject_id"],
            row["project_id"],
            row.get("condition"),
            int(row["age"]) if row["age"] else None,
            row.get("sex"),
            row.get("treatment"),
            row.get("response")
        ))

        # insert into samples
        cursor.execute("""
            INSERT OR IGNORE INTO samples (
                sample_id, subject_id, project_id, sample_type, time_from_treatment_start
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            row["sample_id"],
            row["subject_id"],
            row["project_id"],
            row.get("sample_type"),
            int(row["time_from_treatment_start"]) if row["time_from_treatment_start"] else None
        ))

        # insert into cell_counts
        cursor.execute("""
            INSERT INTO cell_counts (
                sample_id, b_cell, cd8_t_cell, cd4_t_cell, nk_cell, monocyte
            ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            row["sample_id"],
            int(row["b_cell"]) if row["b_cell"] else None,
            int(row["cd8_t_cell"]) if row["cd8_t_cell"] else None,
            int(row["cd4_t_cell"]) if row["cd4_t_cell"] else None,
            int(row["nk_cell"]) if row["nk_cell"] else None,
            int(row["monocyte"]) if row["monocyte"] else None
        ))



#commit and close
connection.commit()
connection.close()

