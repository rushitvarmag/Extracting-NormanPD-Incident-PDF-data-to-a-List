import pytest
import random
from project0.main import insert_incidents, createdb
import sqlite3
import os


# Generate random incidents for testing
def generate_random_incident():
    incident_time = f"2024-08-{random.randint(1, 31):02} {random.randint(0, 23):02}:{random.randint(0, 59):02}"
    incident_number = str(random.randint(10000, 99999))
    location = f"{random.randint(100, 999)} Main St"
    nature = random.choice(['Assault', 'Theft', 'Fraud', 'Vandalism'])
    incident_ori = f"OK{random.randint(10000, 99999)}"
    return {
        'incident_time': incident_time,
        'incident_number': incident_number,
        'incident_location': location,
        'nature': nature,
        'incident_ori': incident_ori
    }

# Test insertion of random incidents into the database
def test_insert_random_incidents():
    db_name = 'resources/test_random_normanpd.db'
    createdb(db_name)

    # Generate a list of random incidents
    random_incidents = [generate_random_incident() for _ in range(10)]

    # Insert random incidents into the database
    insert_incidents(db_name, random_incidents)

    # Verify that the data was inserted correctly
    with sqlite3.connect(db_name) as conn:
        cursor = conn.execute("SELECT * FROM incidents")
        rows = cursor.fetchall()

    assert len(rows) == 10, "Failed to insert all random incidents"

    # Clean up
    if os.path.exists(db_name):
        os.remove(db_name)

