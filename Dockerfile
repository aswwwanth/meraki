FROM python:3.9.1

RUN mkdir /app
WORKDIR /app

ENV FLASK_APP=meraki.py

ADD requirements.txt /app/
ADD entrypoint.sh /app/

RUN pip install -r requirements.txt

RUN chmod +x entrypoint.sh

ENTRYPOINT ["bash"]
CMD [ "entrypoint.sh" ]