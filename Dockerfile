FROM python:3.9.1

ENV ENV='prod'

RUN mkdir /meraki
WORKDIR /meraki

# copy everything except migrations and sock file
COPY . !(*migrations*|meraki.sock) /meraki/

RUN pip install -r requirements.txt
RUN pip install wheel gunicorn eventlet==0.30.2

RUN apt-get update && apt-get install -y nginx

COPY nginx_conf/meraki /etc/nginx/sites-available/meraki
RUN ln -s /etc/nginx/sites-available/meraki /etc/nginx/sites-enabled

RUN chmod +x entrypoint.sh

ENTRYPOINT ["bash"]
CMD [ "entrypoint.sh" ]