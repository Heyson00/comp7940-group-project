FROM python
WORKDIR /app
COPY . /app
RUN pip install update
RUN pip install -r requirements.txt
RUN pip install Flask
RUN pip install pyproject
RUN pip3 install uwsgi

CMD python app.py
