Project Description 
The Norman Police Department offers several reports that showcase both its departmental activities and crime data. In this project, we will input any incident pdf url from the website '[https://www.normanok.gov/public-safety/police-department/crime-prevention-data/department-activity-reports](https://www.normanok.gov/public-safety/police-department/crime-prevention-data/department-activity-reports)' and extract the pdf file data to a list. Then we will create sqllite3 database and insert the list data into the database table. After creation and insertion of data, we will write a query to output Nature of the incidents, sorted by their count and in alphabetical order. All the code and test functions are written using Python and python libraries.

How to Run 
Pip install PyPDF  
Pip install requests  
pipenv run python project0/main.py --incidents https://www.normanok.gov/sites/default/files/documents/2024-08/2024-08-01_daily_incident_summary.pdf
The script will  
Download the pdf file,  
 parse the pdf file to extract the incident data,  
 store the data in a sqlite database,  
 Display a summary of incidents by type .

Functions Overview:

download\_pdf(pdf\_url): Downloads the PDF from the provided URL and saves it locally.

parse\_pdf\_content(): Extracts text from the saved PDF and processes it to remove unnecessary formatting and return clean text.

initialize\_database(): Sets up an SQLite database with a table for storing incident records. If the table already exists, it is dropped and recreated.

insert\_incidents(cursor, connection, raw\_text)**: Parses the extracted text into individual incident records and inserts them into the database.

display\_summary(cursor, connection)**: Queries the database to summarize incident counts by type and displays the results.

Bugs

I had trouble extracting the data from the url
I had trouble in passing testcases
I had trouble in spaces
