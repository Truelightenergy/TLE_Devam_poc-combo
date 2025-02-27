# installation
* install Docker
* install Docker Compose
* install Git
* setup GitHub access
* `git clone git@github.com:Truelightenergy/poc-combo.git poc-combo`
* `cd poc-combo`

# running services
* -- (ignore for now) `docker compose -f ./docker/docker-compose.yml run -d postgres`
* -- (ignore for now) `docker compose -f ./docker/docker-compose.yml up postgres-setup-1`
* `docker compose -f ./docker/docker-compose.yml up postgres-setup-2`
* `docker image build -t tleapi:v0.0.1 -f ./buildContext/src/Dockerfile-trueprice-api ./buildContext/`
* `docker container run -e DATABASE=host.docker.internal -e PGPASSWORD=docker -e PGUSER=docker --name tleapi -d -p 0.0.0.0:5001:5000 tleapi:v0.0.1`
* -- (for linux os) `sudo docker container run -e DATABASE=postgres -e PGPASSWORD=postgres -e PGUSER=postgres --name tleapi -d -p 0.0.0.0:5001:5000 tleapi:v0.0.1`
 * create docker compose build step versus last two lines, if possible
 * `docker container logs -f tleapi`
* `psql -h localhost -U postgres -c 'select * from trueprice.nyiso_forwardcurve;' trueprice` # empty results

# testing service
* open browser to `localhost:5001/upload` and select file to upload
or
* `curl -v -X POST -H "Content-Type: multipart/form-data" -F "file=@buildContext/data/ForwardCurve_NYISO_5X16_20230109_084700.csv" http://localhost:5001/upload`

# checking data
* `psql -h localhost -U postgres`
* -- `postgres=# \l` # show schemas
* `postgres=# \c trueprice` # change schema
* -- `postgres=# \dt trueprice.*` # show tables
* `postgres=# select * from trueprice.nyiso_forwardcurve;`
or 
* `psql -h localhost -U postgres -c 'select * from trueprice.nyiso_forwardcurve;' trueprice` # example

# clean data
* `psql -h localhost -U postgres -c 'truncate trueprice.nyiso_forwardcurve;' trueprice` # example

# clean up
* `docker stop tleapi`
* `docker rm tleapi`
* `docker compose -f ./docker/docker-compose.yml down`


--- 

# local api (on mac)
* `cd github.com/truelightenergy/poc-combo`
* `python3 -m venv .`
* `chmod 700 ./bin/activate`
* `source ./bin/activate`
* `pip3 install -r ./buildContext/src/requirements.txt`

* `DATABASE=$DB_IP PGPASSWORD=docker PGUSER=docker flask --app ./buildContext/src/trueprice_api run --host=0.0.0.0 --post=5001`

do things

* `deactivate`
