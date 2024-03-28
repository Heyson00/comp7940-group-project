FROM python
WORKDIR /app
COPY . /app
RUN pip install update
RUN pip install -r requirements.txt
RUN pip install Flask
RUN pip install gunicorn

EXPOSE 6000

CMD gunicorn --config config.conf app:app