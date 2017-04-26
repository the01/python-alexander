FROM python:2

RUN mkdir /src/

ADD ./actor.py /src/
ADD ./settings_example.yml /src/

RUN pip install alexander_fw -U
# nameko/eventlet/docker bug (https://github.com/nameko/nameko/issues/425)
RUN pip install eventlet==0.20.1
CMD ["python", "/src/actor.py", "run", "actor", "--config", "/src/settings_example.yml"]
