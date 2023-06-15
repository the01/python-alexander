= Alexander Framework

Runtime framework for chat bot/microservice setup based on nameko


== Development

=== Build

=== Test

```shell
pytest -v tests --log-level DEBUG --cov=alexander_fw --cov-branch --cov-report xml:reports/coverage.xml --cov-report=html:reports/coverage --junitxml=reports/pytest.xml --html=reports/pytest.html --self-contained-html
```


```shell
flake8 src
```


```shell
mypy src
```


=== Docker

==== Build

```shell
docker build -t docker.gate.lan/alexander-manager-actor:1.1.0 --build-arg build_version=1.1.0 -f src/manager/actor/Dockerfile .
docker build -t docker.gate.lan/alexander-manager-intent:1.1.0 --build-arg build_version=1.1.0 -f src/manager/intent/Dockerfile .
docker build -t docker.gate.lan/alexander-intent-keyword:0.2.1 --build-arg build_version=0.2.1 -f src/intent/keyword/Dockerfile .
docker build -t docker.gate.lan/alexander-actor-ping:0.2.0 --build-arg build_version=0.2.0 -f examples/actors/ping/Dockerfile .
```


==== Run

```shell
docker run -it --rm --name alex-manager-actor --env-file config/.env docker.gate.lan/alexander-manager-actor:0.2.0
docker run -it --rm --name alex-manager-intent --env-file config/.env docker.gate.lan/alexander-manager-intent:0.2.0
docker run -it --rm --name alex-intent-keyword --env-file config/.env docker.gate.lan/alexander-intent-keyword:0.2.0
```

