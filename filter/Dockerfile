FROM python:3.8
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY /filter.py /app/
WORKDIR /app
CMD ["python", "-u", "filter.py"]