FROM python
WORKDIR /app
COPY . /app
RUN pip install update
RUN pip install -r requirements.txt

CMD python app.py