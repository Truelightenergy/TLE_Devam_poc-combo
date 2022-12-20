Tracking poc for:

* influxdb
* grafana + influxdb
* postgres
* grafana + postgres
* tableau
* tableau + influxdb + 
* tableau + postgres

## influxdb
### set up influxdb

* on mac
  * install binaries (not homebrew)

```
influx_test % ./influxd --reporting-disabled
...
```

```
# note these is created
influx_test % ls ~/.influxdbv2/
configs		engine		influxd.bolt	influxd.sqlite
```

```
# setup user, organization, and initial bucket
influx_test % influx setup        
> Welcome to InfluxDB 2.0!
? Please type your primary username admin
? Please type your password **********
? Please type your password again **********
? Please type your primary organization name truelightenergy
? Please type your primary bucket name trueprice
? Please type your retention period in hours, or 0 for infinite 0
? Setup with these parameters?
  Username:          admin
  Organization:      truelightenergy
  Bucket:            trueprice
  Retention Period:  infinite
 Yes
User	Organization	Bucket
admin	truelightenergy	trueprice
```

```
influxdb2_darwin_amd64 % influx config
Active	Name	URL			Org
*	default	http://localhost:8086	truelightenergy

influxdb2_darwin_amd64 % influx user list
ID			Name
0a6cf51c3c0e4000	admin
```

```
influxdb2_darwin_amd64 % influx user create -n all -o truelightenergy
ID			Name
0a6cf5e1a1ce4000	all
WARN: initial password not set for user, use `influx user password` to set it
```

```
influxdb2_darwin_amd64 % influx user password --name all           
? Please type new password for "all" *********
? Please type new password for "all" again *********
Successfully updated password for user "all"
```

```
influxdb2_darwin_amd64 % influx auth create --all-access --org truelightenergy --user all
ID			Description	Token												User Name	User ID			Permissions
0a6cf705b9ce4000			t84XWlwvzVLoUE4AD7PZZoSuuc32oibDphD86TlPRcrHJiMkfQUi2-ZGvuEi1A3OXX_6aYDordP4VEdStCce8Q==	all		0a6cf5e1a1ce4000	[read:orgs/421f399a38639f91/authorizations write:orgs/421f399a38639f91/authorizations read:orgs/421f399a38639f91/buckets write:orgs/421f399a38639f91/buckets read:orgs/421f399a38639f91/dashboards write:orgs/421f399a38639f91/dashboards read:/orgs/421f399a38639f91 read:orgs/421f399a38639f91/sources write:orgs/421f399a38639f91/sources read:orgs/421f399a38639f91/tasks write:orgs/421f399a38639f91/tasks read:orgs/421f399a38639f91/telegrafs write:orgs/421f399a38639f91/telegrafs read:/users/0a6cf5e1a1ce4000 write:/users/0a6cf5e1a1ce4000 read:orgs/421f399a38639f91/variables write:orgs/421f399a38639f91/variables read:orgs/421f399a38639f91/scrapers write:orgs/421f399a38639f91/scrapers read:orgs/421f399a38639f91/secrets write:orgs/421f399a38639f91/secrets read:orgs/421f399a38639f91/labels write:orgs/421f399a38639f91/labels read:orgs/421f399a38639f91/views write:orgs/421f399a38639f91/views read:orgs/421f399a38639f91/documents write:orgs/421f399a38639f91/documents read:orgs/421f399a38639f91/notificationRules write:orgs/421f399a38639f91/notificationRules read:orgs/421f399a38639f91/notificationEndpoints write:orgs/421f399a38639f91/notificationEndpoints read:orgs/421f399a38639f91/checks write:orgs/421f399a38639f91/checks read:orgs/421f399a38639f91/dbrp write:orgs/421f399a38639f91/dbrp read:orgs/421f399a38639f91/notebooks write:orgs/421f399a38639f91/notebooks read:orgs/421f399a38639f91/annotations write:orgs/421f399a38639f91/annotations read:orgs/421f399a38639f91/remotes write:orgs/421f399a38639f91/remotes read:orgs/421f399a38639f91/replications write:orgs/421f399a38639f91/replications]
```

### write data

```
# using "all" user

```

### read data

```
# using "all" user
```

### update data

### API

### backup

### replicate

### shard

## granfana
### influxdb datasource
### API

## postgres
TimescaleDB is built on postgres
Postgres is hosted in all major clouds
Postgres has sql
### set up postgres

```
postgres_test % docker container run --name some-postgres -e POSTGRES_PASSWORD=postgres -p 0.0.0.0:5432:5432 -d postgres

# for grafana, use host.docker.internal:5432
```

```
postgres_test % docker container exec -it some-postgres psql -U postgres
psql (15.1 (Debian 15.1-1.pgdg110+1))
Type "help" for help.

postgres=#
```

```
postgres=# \db
       List of tablespaces
    Name    |  Owner   | Location 
------------+----------+----------
 pg_default | postgres | 
 pg_global  | postgres | 
(2 rows)
```

### write data

```
postgres=# create database trueprice;
CREATE DATABASE
postgres=# \l
                                                List of databases
   Name    |  Owner   | Encoding |  Collate   |   Ctype    | ICU Locale | Locale Provider |   Access privileges   
-----------+----------+----------+------------+------------+------------+-----------------+-----------------------
 postgres  | postgres | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | 
 template0 | postgres | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | =c/postgres          +
           |          |          |            |            |            |                 | postgres=CTc/postgres
 template1 | postgres | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | =c/postgres          +
           |          |          |            |            |            |                 | postgres=CTc/postgres
 trueprice | postgres | UTF8     | en_US.utf8 | en_US.utf8 |            | libc            | 
(4 rows)

postgres=# \c trueprice;
You are now connected to database "trueprice" as user "postgres".

trueprice=# create table data (id serial PRIMARY KEY, amount numeric(12,8), hour TIMESTAMP);
CREATE TABLE

trueprice=# insert into data (amount, hour) values (1.0, TO_TIMESTAMP('6/1/2022', 'MM/DD/YYYY'));
INSERT 0 1
```

### read data

```
trueprice=# select * from data;
 id |   amount   |        hour         
----+------------+---------------------
  1 | 1.00000000 | 2022-06-01 00:00:00
(1 row)
```

### API
### update data
### backup
### replicate
### shard

## granfana
### postgres datasource
### API

## tableau
### influxdb datasource
### postgres datasource
### API
### tableau management

## volatility notifications
### API
## in-active notifications
### API

## event sourcing