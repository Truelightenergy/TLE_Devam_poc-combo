If all works, this is all that is needed to start:

`docker compose -f "docker-compose.yml" up -d --build`

Sometimes (network issues I think), you might have to run these steps:

`docker compose  -f "docker/docker-compose.yml" up -d --build postgres-setup-1 postgres-setup-2`

Setup minio

`mkdir -p ~/minio/data`
* `docker container run -d -p 9000:9000 -p 9090:9090 --name minio -v ~/minio/data:/data -e "MINIO_ROOT_USER=ROOTNAME" -e "MINIO_ROOT_PASSWORD=CHANGEME123" quay.io/minio/minio server /data --console-address ":9090"`


Grafana needs the postgres datasource added (and dashboards). Here is a blog explaining how that might be accomplished during build time: https://community.grafana.com/t/data-source-on-startup/8618/2