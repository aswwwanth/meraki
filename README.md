# Meraki

## Development

To run the app locally

```
docker-compose up
```

this will run the app and the database in docker containers

For running new migrations attach a shell to the docker container and run the following commands

~~~
flask db migrate
flask db upgrade
~~~

To get a fresh state - delete the docker containers and the `meraki_db_volume` docker volume.