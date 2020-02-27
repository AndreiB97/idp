FROM python:3.8
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY /server.py /app/
WORKDIR /app
CMD ["python", "-u", "server.py"]