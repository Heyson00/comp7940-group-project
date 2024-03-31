FROM python
WORKDIR /app
COPY . /app
RUN pip install update
RUN pip install -r requirements.txt
RUN pip install Flask
RUN pip install gunicorn
RUN pip install --upgrade gevent

CMD gunicorn -c config.py app:app -k 'gevent'
