# cinnamonHAB

## Prerequisites

- Install [docker](https://docs.docker.com/engine/installation/linux/debian/)
- Install [docker compose](https://docs.docker.com/compose/install/)

## OpenHAB server

To start the openhab server run

```
docker-compose pull
docker-compose up [-d]
```

To start the openhab CLI client run

```
docker-compose exec openhab /openhab/runtime/bin/client
```

If you dont't want to use password authentication (home setup), just comment out the following two lines from `openhab.nginx.conf`

```
# auth_basic               "Username applicationnd Password Required";
# auth_basic_user_file     /etc/nginx/.htpasswd;
```

To create users and passwords run `htpasswd -c nginxconfig/htpasswd <your username>` and enter the password when prompted.

After starting the server, you can access it at [http://localhost:8181/](http://localhost:8181/).
