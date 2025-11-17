from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor


table = "yt_api"

def get_conn_cursor():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database="etl_db") #defining the postgres hook
    conn = hook.get_conn() #estaablish the connection
    cur = conn.cursor(cursor_factory=RealDictCursor) #establish the cursor to execute the sql commands, this retuns the dictionary instead of tuple because of cursor_factor=RealDictCursor
    #cur.execute("SELECT * FROM table") #executing the SQL commands
    return conn, cur


def close_conn_cursor(conn, cur):
    cur.close() #close the cursor
    conn.close() #close the connection


def create_schema(schema):
    conn, cur = get_conn_cursor() #establish the connection

    schema_sql = f"CREATE SCHEMA IF NOT EXISTS {schema};"   #creating schema only if the schema does not exist
    cur.execute(schema_sql)
    conn.commit()  #commit the changes
    close_conn_cursor(conn, cur) #close the connection

def create_table(schema):
    conn, cur = get_conn_cursor() #establish the connection

    if schema == 'staging':
        table_sql = f"""
                     CREATE TABLE IF NOT EXISTS {schema}.{table} (
                            "Video_ID" VARCHAR(11) PRIMARY KEY NOT NULL,
                            "Video_Title" TEXT NOT NULL,
                            "Upload_Date" TIMESTAMP NOT NULL,
                            "Duration" VARCHAR(20) NOT NULL,
                            "Video_Views" INT,
                            "Likes_Count" INT,
                            "Comments_Count" INT   
                        );
                    """
    else:
        table_sql = f"""
                  CREATE TABLE IF NOT EXISTS {schema}.{table} (
                      "Video_ID" VARCHAR(11) PRIMARY KEY NOT NULL,
                      "Video_Title" TEXT NOT NULL,
                      "Upload_Date" TIMESTAMP NOT NULL,
                      "Duration" TIME NOT NULL,
                      "Video_Type" VARCHAR(10) NOT NULL,
                      "Video_Views" INT,
                      "Likes_Count" INT,
                      "Comments_Count" INT    
                  ); 
              """

    cur.execute(table_sql)
    conn.commit()
    close_conn_cursor(conn, cur)



def get_video_ids(cur, schema):

    cur.execute(f"""SELECT "Video_ID" FROM {schema}.{table};""")
    ids = cur.fetchall() #this will give dictionary in terms of key value pairs

    video_ids = [row["Video_ID"] for row in ids] #this creates a list and fetches only the value of video_ids

    return video_ids    

