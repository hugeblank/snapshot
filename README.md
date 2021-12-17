# Snapshot
A light photo sharing web app done using [Django](https://www.djangoproject.com/), made beautiful with [Foundation](https://get.foundation/index.html).

This project started as a project for a web development course at my university. Expectations for security, and migration compatibility going forward should be low.

<img src="/screenshots/post.png" width="400">
<img src="/screenshots/user.png" width="400">
<img src="/screenshots/likes.png" width="400">

Note: Screenshots were taken using [Dark Reader](https://darkreader.org/). Dark mode is not natively available, but dark reader is supported, and Snapshot is designed with it in mind.

## Installing

```
git clone https://github.com/hugeblank/snapshot.git
```

### For Production
Before first time setup make sure that:
   1. A file `mysite/mysite/local_settings.py` is created with the following variables:
      - `DEBUG` set to `False`
      - `SECRET_KEY` to a... secret key (spam gibberish if you wish).
      - `ALLOWED_HOSTS` has your domain name(s) or IP(s) in a list (ex: `['snapshot.hugeblank.me', 'example.com']`).
   2. In `Caddyfile` change the name from `snapshot.hugeblank.me` to your domain name or IP. When pulling upstream changes make sure to back up this file, as pulling will overwrite it.

For first time setup:

```
docker-compose build
docker-compose run web /bin/bash
> python manage.py makemigrations
> python manage.py migrate
> python manage.py collectstatic
> exit
```
To start the container:
```
docker-compose up
```

### For Contributing

Before first time setup make sure that:
   1. A file `mysite/mysite/local_settings.py` is created with the following variables:
      - `DEBUG` set to `True`
      - `SECRET_KEY` to a... secret key (spam gibberish if you wish).
      - `ALLOWED_HOSTS` set to an empty list - `[]`
   2. If you want, in `docker-compose.yml`, uncomment lines 11 & 12. This will open port 8000, and allow you to bypass Caddy.
   3. If you're working with Caddy, in `Caddyfile` change the name from `snapshot.hugeblank.me` to `localhost`.

For first time setup:
```
docker-compose build
docker-compose run web /bin/bash
> python manage.py makemigrations
> python manage.py migrate
> python manage.py collectstatic
> exit
```
Note: `python manage.py collectstatic` is an optional step, and can be ignored to if you're not working with Caddy. Consider skipping it if you're not as it creates a `mysite/static` directory that can be very easily confused with the `mysite/hello/static` directory; where static files should go.

To start the container:
```
docker-compose up
```