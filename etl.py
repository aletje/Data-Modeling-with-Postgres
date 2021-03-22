import os
import glob
import psycopg2
import pandas as pd
from sql_queries import *


def process_song_file(cur, filepath):
    """
        Description: 
        - Open, read and extract metadata from JSON files stored in path 'data/song_data'
        - Populate the tables songs and artists 
        
        Arguments:
        - Parameter cur: the cursor object
        - Parameter filepath: metadata filepath
        
        Returns:
        - None
    """
    
    # open song file
    df = pd.read_json(filepath, lines=True)

    # insert song record
    song_data = df.values[[0], [7, 8, 0, 9, 5]]
    cur.execute(song_table_insert, song_data)
    
    # insert artist record
    artist_data = df.values[[0], [0, 4, 2, 1, 3]]
    cur.execute(artist_table_insert, artist_data)


def process_log_file(cur, filepath):
    """
        Description: 
        - Open, read and extract log data from JSON files stored in path 'data/log_data'
        - Populate the tables time, users and songplays

        Arguments:
        - Parameter cur: the cursor object
        - Parameter filepath: log data filepath

        Returns:
        - None
    """
    
    # open log file
    df = pd.read_json(filepath, lines=True)

    # filter by NextSong action
    df = df.loc[df['page'] == "NextSong"]

    # convert timestamp column to datetime
    t = pd.to_datetime(df['ts'], unit='ms')
    
    # insert time data records
    time_data = ([t, t.dt.hour, t.dt.day, t.dt.week, t.dt.month, t.dt.year, t.dt.weekday_name])
    column_labels = (['timestamp', 'hour', 'day', 'week of year', 'month', 'year', 'weekday'])
    time_df = pd.DataFrame({column_labels[i]: time_data[i] for i in range(len(column_labels))})

    for i, row in time_df.iterrows():
        cur.execute(time_table_insert, list(row))

    # load user table
    user_df = pd.DataFrame(df, columns=['userId', 'firstName', 'lastName', 'gender', 'level'])

    # insert user records
    for i, row in user_df.iterrows():
        cur.execute(user_table_insert, row)

    # insert songplay records
    for index, row in df.iterrows():
        
        # get songid and artistid from song and artist tables
        cur.execute(song_select, (row.song, row.artist, row.length))
        results = cur.fetchone()
        
        if results:
            songid, artistid = results
        else:
            songid, artistid = None, None

        # insert songplay record
        songplay_data = (row.sessionId, row.userId, artistid, songid, row.ts, row.level, row.location, row.userAgent)
        cur.execute(songplay_table_insert, songplay_data)


def process_data(cur, conn, filepath, func):
    """
        Description: 
        - Loop through all .json files in directories
        - Append every .json filepath to the all_files list
        - Print the total number of .json files found + the directory path
        - Iterate over each .json file found in 'data/log_data' and execute the ETL-functions in process_log_file
        - Iterate over each .json file found in 'data/song_data' and execute the ETL-functions in process_song_file
        - Finally print the counted value of each succesfully processed .json file

        Arguments:
        - Parameter cur: the cursor object
        - Parameter conn: connection to sparkify db
        - Parameter filepath: path to the directories with .json files
        - Parameter func(cur): the cursor object
        - Parameter func(datafile): each processed datafile in the loop

        Returns:
        - The number of each processed .json file
    """
    
    # get all files matching extension from directory
    all_files = []
    for root, dirs, files in os.walk(filepath):
        files = glob.glob(os.path.join(root,'*.json'))
        for f in files :
            all_files.append(os.path.abspath(f))

    # get total number of files found
    num_files = len(all_files)
    print('{} files found in {}'.format(num_files, filepath))

    # iterate over files and process
    for i, datafile in enumerate(all_files, 1):
        func(cur, datafile)
        conn.commit()
        print('{}/{} files processed.'.format(i, num_files))


def main():
    """
        Description: 
        - Connect to sparkify db
        - Create cursor
        - Call the process_data function
        - Close connection to sparkify db

        Arguments:
        - process_data(cur): cursor object
        - process_date(conn): connection to db
        - process_data(filepath): path to either song or log data directory
        - process_data(func): the ETL function belonging to either song or log data

        Returns:
        - None
    """
    conn = psycopg2.connect("host=127.0.0.1 dbname=sparkifydb user=student password=student")
    cur = conn.cursor()

    process_data(cur, conn, filepath='data/song_data', func=process_song_file)
    process_data(cur, conn, filepath='data/log_data', func=process_log_file)

    conn.close()


if __name__ == "__main__":
    main()