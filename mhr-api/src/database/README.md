# Development Database Setup (Docker)

## Install postgreSQL from scratch:
Skip to step 7 if using an existing instance.
1. docker pull postgres
2. docker images
3. docker volume create postgres-data
4. docker volume ls
5. docker run --name postgres-container -e POSTGRES_PASSWORD={password} -p {port}:5432 -v postgres-data:/var/lib/postgresql/data -d postgres:latest
6. docker ps
7. docker exec -it postgres-container psql -U postgres

        CREATE DATABASE ppr;
        \list
        quit

## Remove Install:
1. docker stop postgres-container
1. docker rm postgres-container
1. docker rmi postgres
1. docker volume rm postgres-data


## Data Model Diagram
![DOC Service Data Model ](doc_postgres.png "Document Service Data Model")

