FROM python:3

ADD tide-water-level-exporter.py /

RUN pip install requests prometheus_client

CMD [ "python", "./tide-water-level-exporter.py" ]
