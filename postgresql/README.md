# Sistema de Gestão de Dados - Postgresql Demo

This code is to be used in the scope of the _SGD_ course.


## Requirements

- To execute this project it is required to have installed:
  - Docker

## Development

Use only if you need to have database running in separate. 
The executables in the root are preparared to start the database and connect it with Web Application.

It could be useful to have it running in separate for the Java example, where it is not possible for you to change code being executed by Docker and access does changes without starting docker components again.

## Database Connection

- **User**: SGD_project
- **Password**: 5432
- **Database name**: cloud_query
- **Host**: localhost:5433

## Setup and Run

To build the docker image you should run:

```sh
sh build.sh
```

To run the container:

```sh
sh run.sh
```

- _note: modifying the `run.sh` script to include -dit will make the container work in background. But dont forget to use `stop.sh` to stop/remove it later._

To stop the container:

```sh
sh stop.sh
```


## Authors

* SGD 2021 Team
* University of Coimbra

