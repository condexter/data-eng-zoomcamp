#!/usr/bin/env python
# coding: utf-8

import os
import argparse
import pandas as pd
from sqlalchemy import create_engine
from time import time

def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    url = params.url
    table_name = params.table_name

    csv_name = 'output.csv'

    #download the csv

    os.system(f"wget {url} -O {csv_name}")

    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    df_iter = pd.read_csv(csv_name, iterator=True, chunksize=100000)
    df = next(df_iter)

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
    
    df.head(n=0).to_sql(name=table_name, con=engine, if_exists='replace')

    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        try:
            t_start = time()
            df = next(df_iter)
            
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)
            
            df.to_sql(name=table_name, con=engine, if_exists='append')
            
            t_end = time()
            
            print('inserted another chunk..., took %.3f seconds' % (t_end - t_start))
        except:
            print('Finished ingesting data into the postgres database')
            break

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres.')

    # user, password, host, port, database name, table name, url of the csv

    parser.add_argument('--user', help='user name')
    parser.add_argument('--password', help='password')
    parser.add_argument('--host', help='host')
    parser.add_argument('--port', help='port')
    parser.add_argument('--db', help='database name')
    parser.add_argument('--table_name', help='table name')
    parser.add_argument('--url', help='csv url')

    args = parser.parse_args()
    main(args)



