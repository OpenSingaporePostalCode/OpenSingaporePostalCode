import csv
import logging
import os

import pymongo


def _get_uri():
    username = os.environ.get('MONGODB_USER')
    password = os.environ.get('MONGODB_PASSWORD')
    hostname = os.environ.get('MONGODB_HOST')
    db_name = os.environ.get('MONGODB_NAME')

    logging.info('username=%s', username)
    logging.info('hostname=%s', hostname)
    logging.info('db_name=%s', db_name)

    if not username or not password or not hostname or not db_name:
        logging.error('incomplete mongodb config')

    return f"mongodb+srv://{username}:{password}@{hostname}/{db_name}?retryWrites=true&w=majority"


if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s [%(levelname)s] %(name)s - %(message)s',
                        encoding='utf-8', level=logging.DEBUG)

    client = pymongo.MongoClient(_get_uri())
    db = client.raw
    codes = db.codes

    mapping = {}

    for code in codes.find({'found': {'$gt': 0}}):
        for result in code['results']:
            postal = result['POSTAL']
            if postal and len(postal) != 6:
                logging.warning('invalid postal=%s; skipping', postal)
                continue 

            road_name = result['ROAD_NAME']

            mismatched = postal in mapping and  mapping[postal] != road_name
            logging.warning('postal=%s mismatch road name') if mismatched else True

            mapping[postal] = road_name

    with open('road_name.csv', 'w') as csv_file:
        fieldnames = ['code', 'name']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        writer.writeheader()
        for k, v in mapping.items():
            writer.writerow({'code': k, 'name': v})
