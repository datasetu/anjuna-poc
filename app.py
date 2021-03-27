import io
import os

import boto3
import pandas as pd
import pandasql as ps
import requests


# Initialise a few constants
REGION              =   'ap-south-1'
ACCESS_KEY_ID       =   os.environ['ACCESS_KEY_ID']
SECRET_ACCESS_KEY   =   os.environ['SECRET_ACCESS_KEY']
BUCKET_NAME         =   os.environ['BUCKET_NAME']
OBJECT_KEY          =   os.environ['OBJECT_KEY']
SLACK_TOKEN         =   os.environ['SLACK_TOKEN']
SLACK_CHANNEL       =   '#general'
SLACK_USER_NAME     =   'Enclave Bot'
SLACK_URL           =   'https://slack.com/api/files.upload'
OUTPUT_FILENAME     =   'results.csv'
OUTPUT_FILETYPE     =   'csv'

print(ACCESS_KEY_ID, SECRET_ACCESS_KEY, BUCKET_NAME, OBJECT_KEY)


# This is a simple query that runs over the confidential data.
QUERY               = \
'''
select (case when lower(crimedescr) like '%dui%' then 'DUI' when lower(crimedescr) like '%burglary%' then 'burglary' when lower(crimedescr) like '%homicide%' then 'homicide' when lower(crimedescr) like '%narcotics%' then 'narcotics' when lower(crimedescr) like '%missing person%' then 'missing_person_reports' when lower(crimedescr) like '%traffic-accident%' then 'traffic_accidents' end) as crime_type, count(*) as incident_counts from df where crime_type is not null group by crime_type;
'''

# Read the sacramento crime reports file from S3
s3c =   boto3.client(
            's3',
            region_name=REGION,
            aws_access_key_id=ACCESS_KEY_ID,
            aws_secret_access_key=SECRET_ACCESS_KEY
        )

obj = s3c.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY)
df  = pd.read_csv(io.BytesIO(obj['Body'].read()), encoding='utf8')

# Run the SQL query over the data in memory. This can be afforded as the data is very small in size
result  = ps.sqldf(QUERY, locals())

#Convert results to CSV
result.to_csv('results.csv')

print(result)

# Initialise rest of the necessary slack vars
SLACK_FILE_PAYLOAD  =   {
                            'file' : (OUTPUT_FILENAME, open(OUTPUT_FILENAME, 'rb'), OUTPUT_FILETYPE)
                        }
SLACK_PARAMS        =   {
                            'filename': OUTPUT_FILENAME,
                            'token': SLACK_TOKEN,
                            'channels': ['#general']
                        }

# Post the results to a slack channel
try:
    r = requests.post(SLACK_URL, params=SLACK_PARAMS, files=SLACK_FILE_PAYLOAD)
except Exception as e:
    print('Error posting to slack', e)
