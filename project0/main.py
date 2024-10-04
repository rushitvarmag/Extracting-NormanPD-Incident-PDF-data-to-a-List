import argparse
import requests
from io import BytesIO
import sqlite3
import re
import os
from pypdf import PdfReader


def main(url):
    # Step 1: Download the PDF file
    pdf_content = fetchincidents(url)

    # Step 2: Extract incident data from the PDF
    extracted_data = extractincidents(pdf_content)

    # Step 3: Create the SQLite database in the 'resources' directory
    db_name = 'resources/normanpd.db'
    createdb(db_name)

    # Step 4: Insert the extracted data into the database
    populatedb(db_name, extracted_data)

    # Step 5: Print the counts of each incident type in alphabetical order
    status(db_name)


# Fetch PDF content from URL
def fetchincidents(url):
    return retrieve_pdf(url)


# Function to download the PDF file and return its content
def retrieve_pdf(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return BytesIO(response.content)
    except requests.RequestException as e:
        raise Exception(f"PDF retrieval failed: {str(e)}")


# Parse incidents from PDF using regex
def extractincidents(pdf_file):
    return parse_incidents(pdf_file)


# Function to parse incidents from the PDF using regex
def parse_incidents(pdf_content):
    reader = PdfReader(pdf_content)
    full_text = ""

    # Extract text from all pages
    for page in reader.pages:
        full_text += page.extract_text()

    # Split text into lines for easier handling of multi-line incidents
    lines = full_text.splitlines()

    # Regex pattern to match incidents
    incident_regex = re.compile(
        r'(\d{1,2}/\d{1,2}/\d{4}\s+\d{1,2}:\d{2})\s+'  # Date and time
        r'(\d{4}-\d{8})\s+'  # Incident number
        r'(.+?)(?:\n(?!\d{1,2}/\d{1,2}/\d{4}).+)*?\s+'  # Incident location
        r'(Traffic Stop|Suspicious|Missing Person|Kidnapping|Assist EMS|Headache|Fire Fuel Spill|Fire Carbon Monoxide Alarm|COP Problem Solving|Officer in Danger|Assist Fire|Assault|Fire Transformer Blown|Fire Mutual Aid|Bar Check|Test Call|Animal Vicious|Back Pain|Fire Dumpster|Preg/Child Birth/Miscarriage|Welfare Check|Bomb/Threats/Package|Special Assignment|Prowler|Burns/Explosions|EMS Mutual Aid|Homicide|Stand By EMS|Loud Party|Molesting|Fire Residential|Cardiac Respritory Arrest|Body Reported|Animal Livestock|Traumatic Injury|Reckless Driving|Shooting Stabbing Penetrating|Carbon Mon/Inhalation/HazMat|Foot Patrol|Transfer/Interfacility|Animal Trapped|Choking|Burglary|COP Relationships|Unknown Problem/Man Down|Officer Needed Nature Unk|Barking Dog|Animal Bites/Attacks|Warrant Service|Contact a Subject|Disturbance/Domestic|Motorist Assist|Noise Complaint|Larceny|Trespassing|Unconscious/Fainting|Medical Call Pd Requested|Shots Heard|Alarm|Supplement Report|Convulsion/Seizure|MVA With Injuries|Overdose/Poisoning|Mutual Aid|Diabetic Problems|Heat/Cold Exposure|Breathing Problems|Public Assist|Runaway or Lost Child|Chest Pain|MVA Non Injury|Public Intoxication|Stroke|Open Door/Premises Check|Check Area|Vandalism|Animal Complaint|Animal Dead|Fire Alarm|Follow Up|Item Assignment|Animal Injured|Fraud|Pick Up Partner|Supplement Report|911 Call Nature Unknown|Falls|Escort/Transport|Animal at Large|Parking Problem|Abdominal Pains/Problems|Indecent Exposure|Animal Bite|Hit and Run|Stolen Vehicle|Sick Person|Harassment / Threats Report|Fire Grass|Assault EMS Needed|Alarm Holdup/Panic|Fight|Fire Smoke Investigation|Heart Problems/AICD|Fire Commercial|Fire Electrical Check|COP DDACTS|Fire Odor Investigation|Extra Patrol|Fire Controlled Burn|Civil Standby|Drunk Driver|Hemorrhage/Lacerations|Warrant Service|Debris in Roadway|Pick Up Items|Found Item|Stand By EMS|Stake Out|Unknown Problem/Man Down|Officer Needed Nature|Assist Police|Unk|Allergies/Envenomations|Road Rage|Fire Carbon Monoxide Alarm|Fire Water Rescue|Fire Down Power Line|Fire Gas Leak|Drowning/Diving/Scuba Accident|Cardiac Respiratory Arrest|Drug Violation|Loud Party)\s+'  # Nature
        r'(OK0140200|14005|EMSSTAT|14009|COMMAND)'  # Incident ORI
    )

    # Extract the incidents using regex
    incidents = []
    current_location = None

    for line in lines:
        # Skip headers and irrelevant lines
        if "Daily Incident Summary" in line or line.startswith("Date / Time Incident"):
            continue

        # Check if the line starts a new incident with a date pattern
        if re.match(r'\d{1,2}/\d{1,2}/\d{4}', line):
            current_location = line  # Update current location

            # Match incident pattern
            match = re.match(incident_regex, line)
            if match:
                incidents.append(match.groups())

        # Handle multi-line incidents (append to previous line)
        elif current_location:
            current_location += f" {line.strip()}"
            match = re.match(incident_regex, current_location)
            if match:
                incidents.append(match.groups())
                current_location = None  # Reset after matching

    return incidents


# Initialize the database and create table in 'resources' directory
def createdb(db_name):
    # Ensure the 'resources' directory exists
    initialize_database(db_name)


# Function to initialize the SQLite database
def initialize_database(db_name):
    resources_dir = os.path.dirname(db_name)
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)

    with sqlite3.connect(db_name) as conn:
        conn.execute('DROP TABLE IF EXISTS incidents')
        conn.execute('''
        CREATE TABLE incidents (
            incident_time TEXT,
            incident_number TEXT,
            incident_location TEXT,
            nature TEXT,
            incident_ori TEXT
        )
        ''')


# Insert extracted data into the database
def populatedb(db_name, incidents):
    insert_incidents(db_name, incidents)


# Function to insert incidents data into SQLite database
def insert_incidents(db_name, incidents_data):
    with sqlite3.connect(db_name) as conn:
        conn.executemany(
            'INSERT INTO incidents VALUES (?, ?, ?, ?, ?)',
            incidents_data
        )


# Print incident summary
def status(db_name):
    display_incident_stats(db_name)


# Function to display incident statistics
def display_incident_stats(db_name):
    with sqlite3.connect(db_name) as conn:
        cursor = conn.execute(
            'SELECT nature, COUNT(*) FROM incidents GROUP BY nature ORDER BY nature'
        )
        for nature, count in cursor:
            print(f"{nature}|{count}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--incidents", type=str, required=True, help="URL of the incident PDF.")
    args = parser.parse_args()

    if args.incidents:
        main(args.incidents)
