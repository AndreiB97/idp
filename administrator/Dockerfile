FROM python:3.8
COPY requirements.txt /tmp
RUN pip install -r /tmp/requirements.txt
COPY /administrator.py /app/
WORKDIR /app
CMD ["python", "-u", "administrator.py"]