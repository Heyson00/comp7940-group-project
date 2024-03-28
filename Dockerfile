FROM python
WORKDIR /app
COPY . /app
RUN pip install update
RUN pip install -r requirements.txt
RUN pip install Flask
RUN pip install gunicorn

CMD python app.py
CMD gunicorn -w 3 -b 127.0.0.1:5050 app:app
