ARG AIRFLOW_VERSION=2.9.0
#defining airflow version
ARG PYTHON_VERSION=3.10   
#defining python version

FROM apache/airflow:${AIRFLOW_VERSION}-python${PYTHON_VERSION}  
#Choose the base image dynamically using the above variables
#The official image is published and maintained by the Apache Airflow project on Docker Hub
#The Airflow image is a Docker image built for Apache Airflow.

ENV AIRFLOW_HOME=/opt/airflow
#Set environment variable (available at runtime)

COPY requirements.txt /   
#copy requirements from local to root directory of the docker images file system

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt   

#pip does cache the packages which keeps the image size smaller
