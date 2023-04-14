# bib-lite
BibXML service with SQLite backend


## Administration

### Run server
```
docker-compose up --build -d
```

### Load data

```
docker exec -ti bib-lite-python python scripts/load-data.py '/app/bib.db' '/app/relaton-data-rfcs/data'
docker exec -ti bib-lite-python python scripts/load-data.py '/app/bib.db' '/app/relaton-data-ids/data'
```
