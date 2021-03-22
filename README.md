# Project Summary 
- Created 1 fact and 4 dimension tables in a Postgres database
- Created an ETL pipeline that transfers data from JSON files in two local directories into the fact and dimension tables
- Created a small dashboard for visualizing unique listeners per day 

#### Running the scripts

##### ETL-jobs
- Open a new Ipython notebook and run the commands in the following order
    - `%run create_tables.py`
    - `%run etl.py`

##### Dashboard
- Make sure the database is populated by running the `ETL-jobs` above
- Open `dashboard.ipynb` and run the commands sequentially

# sparkifydb
#### Purpose
This database is designed for analysing song plays from Sparkify app

#### Database schema design
- Fact table 
    - `songplays` are records in log data associated with song plays i.e. records with page NextSong
- Dimension tables
    - `users` are users in the app
    - `songs`  are songs from music metadata database
    - `artists` are artists from music metadata database
    - `time` are timestamps of records in songplays broken down into specific units
    
#### ETL pipeline
The ETL pipeline `etl.py` using Python and Postgres SQL, transfers data from files in two local directories:
- Song JSON metadata files in `data/song_data` populates `songs` and `artists` tables
- Log JSON files in `data/log_data` populates `users`, `time` and `songplays` tables

#### Example queries
##### Fetch fact row with an artist_id and song_id
`SELECT * FROM songplays WHERE artist_id != 0`

##### Count unique and active users who is paying for the service
`SELECT count(f.*) as cnt, d.user_id, d.level
 FROM songplays f 
 INNER JOIN users d ON d.user_id = f.user_id
 GROUP BY d.user_id, d.level
 HAVING level='paid'`