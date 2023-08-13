FROM apache/airflow:2.6.1

USER root

RUN apt-get update && apt-get -y upgrade

RUN apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

#RUN apt-get update && apt-get install apt-transport-https && apt-get install ca-certificates -y \
#    && apt-get install curl -y && apt-get install gnupg -y && apt-get install apt-utils -y
#    && apt-get install python3 -y  && ln -s /usr/bin/python3 /usr/bin/python
#
#RUN echo "deb https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
#    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
#    && apt-get update && apt-get install google-cloud-cli -y
COPY requirements.txt /

USER airflow

RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
