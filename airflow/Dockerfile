# airflow/Dockerfile
FROM apache/airflow:2.5.1-python3.9

USER root

# Install any additional packages needed
RUN apt-get update && apt-get install -y \
    vim \
    git \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Copy DAGs and scripts
COPY dags /opt/airflow/dags
COPY scripts /opt/airflow/scripts

# Set the entrypoint
ENTRYPOINT ["tini", "--", "entrypoint"]
CMD ["webserver"]
