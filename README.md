Juniper Firefly Resource Adapter

## virtualenv

### Development

* To run the adapter in development environment:
```
git clone git@github.cyanoptics.com:orchestrate/bp-ra-firefly.git bp-ra-firefly
cd bp-ra-firefly
make prepare-venv
source env/bin/activate
bprafirefly
```

* Running Tests:
```
make test
```

### Running simulator

To start the simulator:
```
$ source env/bin/activate
(env)$ bpprov-sim juniper/model/sim mx960 --web_port=8081 --db mx960_1
```

Now connect to the Juniper MX960 Sim via netconf(username: admin, password: admin):
```
$ ssh -p 7777 admin@localhost netconf
```

Establish session:
```
$ curl -H "Content-Type: application/json" -d '{"authentication": {"netconf": {"username": "admin", "password": "admin"}}, "connection": {"hostname": "localhost", "netconf": {"hostport": 7777}}, "typeGroup": "/typeGroups/Juniper", "id": "1"}' http://localhost:8080/api/v1/sessions
```

## Docker

### Basic Operation

```
make image
make start
```

Notice, "make start" launches the detached container in the background.  "make stop" stops the container. Use "make run" to launch in foreground"

### Test

Assuming you have made the image already, use the make targets beginning with "d" to test.

```
make dtest
```

### Development

The makefile has support to make a development image where your code is mounted inside the docker container.  This allows a developer to iterate quickly without rebuilding a docker container each time.  The other makefile targets for running and testing will detect the development image and behave accordingly.

```
make image-dev
```

In development mode, and requirements listed in requirements-src.txt are installed and directly to .src.  This is a good opportununity to include dependent libraries as an editable git repository.

### Launching Simulators

The simulator docker image is seperate from the main ea docker image. Launch scripts, docker-start-sim and docker-stop-sims, are provided.  The start script take a single parameter for the elementType.

```
make image-sim
scripts/docker-start-sim mx960
```

### Other

Use "make help" for a complete list of current support targets.
