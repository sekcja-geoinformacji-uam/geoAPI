FROM python:3.9
RUN apt-get update && apt install -y libgdal-dev
COPY ./requirements.txt /requirements.txt
COPY ./app.py /app.py
RUN pip install -r requirements.txt
CMD ["python3", "app.py"]
