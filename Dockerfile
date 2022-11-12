FROM python:3.9-alpine3.16
COPY ./requirements.txt /requirements.txt
COPY ./app.py /app.py
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]
