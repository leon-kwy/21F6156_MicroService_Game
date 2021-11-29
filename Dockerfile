WORKDIR /app

RUN pip3 freeze > requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

CMD [ "python3", "app.py" ]
