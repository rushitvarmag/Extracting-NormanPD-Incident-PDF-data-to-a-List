import argparse
import requests
from io import BytesIO
import sqlite3
import re
import os  # To handle file paths and directory creation
from pypdf import PdfReader


def main(url):
   # Step 1: Download the PDF file
   pdf_content = fetchincidents(url)

   # Step 2: Extract incident data from the PDF
   extracted_data = extract_incidents(pdf_content)

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
def extract_incidents(file_path):
   # PDF Loading
   reader = PdfReader(file_path)

   # extracting text data from all pages
   text_data = [page.extract_text(extraction_mode="layout") for page in reader.pages]

   # Parsing all the incidents using double spaces (more than one double space can be used) to separate columns
   incidents = []
   # Variable to track if the header is skipped or not
   header_skipped = False

   for page_text in text_data:
       # Splitting the page text into lines
       lines = page_text.split('\n')
       for line in lines:
           # Using double spaces for splitting of columns
           columns = re.split(r'\s{2,}', line.strip())

           # Ensuring that all columns exist to match the expected number of fields
           if len(columns) >= 5:
               # Skip the first row if it is the header
               if not header_skipped:
                   header_skipped = True
                   continue

               # Opening the columns in the following order:
               # Date / Time | Incident Number | Location | Nature | Incident ORI
               date_time, incident_number, location, nature, incident_ori = map(str.strip, columns[:5])

               # Appending incident data as a dictionary
               incidents.append({
                   'incident_time': date_time,
                   'incident_number': incident_number,
                   'incident_location': location,
                   'nature': nature,
                   'incident_ori': incident_ori
               })

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
           [(incident['incident_time'], incident['incident_number'], incident['incident_location'], incident['nature'], incident['incident_ori']) for incident in incidents_data]
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
