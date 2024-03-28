FROM python
WORKDIR /app
COPY . /app
RUN pip install update
RUN pip install -r requirements.txt
RUN pip install Flask
RUN pip install gunicorn

CMD gunicorn -c gunicorn.py app:app
# CMD python app.py