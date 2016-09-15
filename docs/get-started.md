### prepare for AuthHub

  * db and cache

    AuthHub use postgresql to manage data, use memcache to store session, you need
    have postgresql and memcache configure and installed before development.

  * init database authhub

    + create database (with dbname authhub, username authhubadm)

      ```
      create user authhubadm with password 'zhu88jie'
      create database authhub owner authhubadm
      ```
    + config alembic.ini

      ```
      cd authhub/authhub/db/migration
      vim alembic.ini
      ```
      sqlalchemy.url =postgresql://authhubadm:AUTHHUB_DB_PASSWORD@AUTHHUB_DB_HOST:5432/authhub

      replace AUTHHUB_DB_HOST and AUTHHUB_DB_PASSWORD with your postgresql's db ipaddress and password

    + create database tables

      ```
      cd authhub/authhub/db/migration
      alembic revision --autogenerate -m 'init authhub table'
      alembic upgrade head
      ```

  * configure /opt/zen/conf/authhub.yaml

      ```
      memcache:
        - YOUR_MEMCACHE_SERVER_IP:YOUR_MEMCACHE_PORT
      postgres:
        host: YOUR_PG_HOST
        passwd: YOUR_PG_PASSWORD
      log:
        level: debug
        verbose: True
      ```

      replace YOUR_MEMCACHE_SERVER_IP, YOUR_MEMCACHE_PORT, YOUR_PG_HOST with your
      configuration like below:

      ```
      memcache:
       - 127.0.0.1:11211
      postgres:
       host: 127.0.0.1
       passwd: zhu88jie
      log:
       level: debug
       verbose: True
      ```

  * log is located at /opt/zen/logs/authhub.log

### Try AuthHub with docker image (within authhub-docker folder)

   * cd authhub-docker, make sure Dockerfile is under this folder
   * Follow this project's README doc to build docker images and run docker containers for AuthHub

### Develop with virtualenv

   * sudo pip install virtualenv
   * cd authhub, make sure manage.py is in this folder
   * virtualenv env
   * source env/bin/activate
   * pip install -r requirements.txt
   * add **authhub/** to PYTHONPATH
   * python manage.py runserver
