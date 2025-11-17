from airflow import DAG
import pendulum #for deaing with different timezoness
from datetime import datetime, timedelta
from api.video_stats import get_playlist_id, get_video_ids, extract_video_data, save_to_json
from airflow.operators.trigger_dagrun import TriggerDagRunOperator

from api.video_stats import (
    get_playlist_id,
    get_video_ids,
    extract_video_data,
    save_to_json,
)

from datawarehouse.dwh import staging_table, core_table
from dataquality.soda import yt_elt_data_quality

# Define the local timezone
local_tz = pendulum.timezone("Europe/Malta") #use your timezone where you are running the code

# Default Args
default_args = {
    "owner": "dataengineers",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "data@engineers.com",
    # 'retries': 1,
    # 'retry_delay': timedelta(minutes=5),
    "max_active_runs": 1,
    "dagrun_timeout": timedelta(hours=1),
    "start_date": datetime(2025, 1, 1, tzinfo=local_tz),  #the time at which the airflow will begin running the DAG, but the first run will be scheduled at the end of the interval following the start date
    #for example if the start date is 1st Jan 2025 midnight the actual DAG will be on 2nd of Jan which is the end of the first interval following the start date
    # 'end_date': datetime(2030, 12, 31, tzinfo=local_tz),
}

#variables
staging_schema = "staging"
core_schema = "core"

#writing DAG
with DAG(
    dag_id='produce_json',
    default_args=default_args,
    description='DAG to produce json file with raw data',
    schedule='0 14 * * *',  #at 2pm
    catchup=False, #tells airflow to not catchup the missed diagrams from past

) as dag_produce: 
    
    #define tasks by calling the functions defined in video_stats.py
    playlist_id=get_playlist_id()
    video_ids=get_video_ids(playlist_id)
    extracted_data=extract_video_data(video_ids)
    save_to_json_task=save_to_json(extracted_data)

    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_json",
        trigger_dag_id="update_json",
    )

    #define file dependencies
    #In what order the tasks run from left to right task_a() >> task_b() >> task_c()
    playlist_id >> video_ids >> extracted_data >> save_to_json_task >> trigger_update_db


with DAG(
    dag_id='update_json',
    default_args=default_args,
    description='DAG to produce json file and insert data into both staging and core schemas',
    schedule=None,  #'0 15 * * *',  #at 3pm
    catchup=False, #tells airflow to not catchup the missed diagrams from past

) as dag_update: 
    #define tasks by calling the functions defined in video_stats.py
    update_staging = staging_table()
    update_core = core_table()

    trigger_data_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality",
    )

    #define file dependencies
    #In what order the tasks run from left to right task_a() >> task_b() >> task_c()
    update_staging >> update_core >> trigger_data_quality    


with DAG(
    dag_id='data_quality',
    default_args=default_args,
    description='DAG to check the data quality on both layers in the db',
    schedule=None, #'0 16 * * *',  #at 3pm
    catchup=False, #tells airflow to not catchup the missed diagrams from past

) as dag_quality: 

    #define tasks by calling the functions defined in video_stats.py
    soda_validate_staging = yt_elt_data_quality(staging_schema)
    soda_validate_core = yt_elt_data_quality(core_schema)

    #define file dependencies
    #In what order the tasks run from left to right task_a() >> task_b() >> task_c()
    soda_validate_staging >> soda_validate_core 