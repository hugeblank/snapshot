# Assignment 4
 A light instagram-like application done using django models and forms, made beautiful with foundation.

<img src="/screenshots/menu1.png" width="400"><img src="/screenshots/menu2.png" width="400">
<img src="/screenshots/post.png" width="400"><img src="/screenshots/comment.png" width="400">
<img src="/screenshots/register.png" width="400"><img src="/screenshots/login.png" width="400">

## Installation

```
docker-compose build
docker-compose run web /bin/bash
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```

If a production server make sure that:
 - In `mysite/mysite/settings.py`:
    - `DEBUG` is set to `False`
    - `SECRET_KEY` is changed from the default.
    - `ALLOWED_HOSTS` has your domain name or IP.
 - In `docker-compose.yml` lines 11 & 12 (ports [le forbidden backdoor]) are removed
 - In `Caddyfile` change the name of `localhost` to your domain name or IP.