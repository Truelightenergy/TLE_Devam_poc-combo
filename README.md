# Production

System resides in AWS us-east-2 region. Consists of 1 EC2 instance ()

## Production Database
* Postgres 15
* db truprice `postgres=> \c trueprice`
* schema trueprice
* tables
```
trueprice=> \dt+ trueprice.*
                                               List of relations
  Schema   |          Name           | Type  | Owner  | Persistence | Access method |    Size    | Description 
-----------+-------------------------+-------+--------+-------------+---------------+------------+-------------
 trueprice | ercot_energy            | table | docker | permanent   | heap          | 256 kB     | 
 trueprice | ercot_energy_history    | table | docker | permanent   | heap          | 136 kB     | 
 trueprice | ercot_nonenergy         | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | ercot_nonenergy_history | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | ercot_rec               | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | ercot_rec_history       | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | isone_energy            | table | docker | permanent   | heap          | 264 kB     | 
 trueprice | isone_energy_history    | table | docker | permanent   | heap          | 120 kB     | 
 trueprice | isone_nonenergy         | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | isone_nonenergy_history | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | isone_rec               | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | isone_rec_history       | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | miso_energy             | table | docker | permanent   | heap          | 200 kB     | 
 trueprice | miso_energy_history     | table | docker | permanent   | heap          | 104 kB     | 
 trueprice | nyiso_energy            | table | docker | permanent   | heap          | 264 kB     | 
 trueprice | nyiso_energy_history    | table | docker | permanent   | heap          | 136 kB     | 
 trueprice | nyiso_rec               | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | nyiso_rec_history       | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | pjm_energy              | table | docker | permanent   | heap          | 440 kB     | 
 trueprice | pjm_energy_history      | table | docker | permanent   | heap          | 200 kB     | 
 trueprice | pjm_nonenergy           | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | pjm_nonenergy_history   | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | pjm_rec                 | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | pjm_rec_history         | table | docker | permanent   | heap          | 0 bytes    | 
 trueprice | site                    | table | docker | permanent   | heap          | 8192 bytes | 
 trueprice | uploads                 | table | docker | permanent   | heap          | 16 kB      | 
 trueprice | users                   | table | docker | permanent   | heap          | 16 kB      | 
(27 rows)
```
* Custom DB Parameter group (ron-reduce-tls-pgcat)
  * `rds.force_ssl` = 0 (allow non SSL)
* private network access only
  * logs enabled
* TLS disabled (until proxy - pgcat - is configured to use it)
* admin user = postgres
* admin password managed by AWS Secrets Manager
  * auto rotated weekly
* connect example
  * `psql -h poc-combo.cdcasjjgwquj.us-east-2.rds.amazonaws.com  -p 5432 -U postgres postgres`
* application user = docker
* application password = docker
* type db.m6i.large
* not multi-zone (cost)

## Production Virtual Machine
* Static IP (EIP) - 3.128.236.232
* Ubuntu 22.04
* Two firewalls
  * To Application below - `sg-0845b17f8a6c42a24 - ercot-poc`
  * Application to database - `sg-06a3c09d03fb11825 - ec2-rds-1`
* S3 access is provided to application via a Instance Profile (arn:aws:iam::054441241273:role/tle-trueprice)

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "arn:aws:iam::054441241273:role/tle-trueprice"
        },
        {
            "Sid": "VisualEditor1",
            "Effect": "Allow",
            "Action": "s3:*",
            "Resource": "arn:aws:s3:::tle-trueprice-api-source-data/*"
        }
    ]
}
```

## Application

* Flask based, using venv to manage dependencies (see usage below)
* code https://github.com/Truelightenergy/poc-combo
* Deployed manually as Git repo
* Example upgrade code session
  * `ubuntu@ip-172-31-41-181:~$ cd github.com/truelightenergy/poc-combo/`
  * `ubuntu@ip-172-31-41-181:~/github.com/truelightenergy/poc-combo$`
  * `ubuntu@ip-172-31-41-181:~/github.com/truelightenergy/poc-combo$ source ./app_env/bin/activate`
  * Upgrade - kill existing flask process
  * `GIT_SSH_COMMAND='ssh -i ~/.ssh/tle_poc_combo_ed25519 -o IdentitiesOnly=yes' git pull`
    * Note the use of "deployment key" (allows us to pull from GH but not push)
  * if needed - `pip3 install -r ./buildContext/src/requirements.txt`
  * if needed - update database per changes here `docker/docker-compose.yml`
  * `/github.com/truelightenergy/poc-combo$ DATABASE=poc-combo.cdcasjjgwquj.us-east-2.rds.amazonaws.com PGPASSWORD=docker PGUSER=docker nohup flask --app ./buildContext/src/trueprice_api run --cert=adhoc --host=0.0.0.0 --port=2345 > flask.log 2>&1 &`

# Development (needs refresh)

If all works, this is all that is needed to start:

`docker compose -f "docker-compose.yml" up -d --build`

Sometimes (network issues I think), you might have to run these steps:

`docker compose  -f "docker/docker-compose.yml" up -d --build postgres-setup-1 postgres-setup-2`

Setup minio

`mkdir -p ~/minio/data`
* `docker container run -d -p 9000:9000 -p 9090:9090 --name minio -v ~/minio/data:/data -e "MINIO_ROOT_USER=ROOTNAME" -e "MINIO_ROOT_PASSWORD=CHANGEME123" quay.io/minio/minio server /data --console-address ":9090"`


Grafana needs the postgres datasource added (and dashboards). Here is a blog explaining how that might be accomplished during build time: https://community.grafana.com/t/data-source-on-startup/8618/2

# Activity

* 21-May-2023 (major update)
  * rename prior database (users)
  * rebuild database (lots of SQL changes, wanted to not get bogged down in alters -- and to reconfirm we are in command of DB setup)
  * pull hundreds of changes (UI mostly, new headers, bug fixes, etc.)
  * test