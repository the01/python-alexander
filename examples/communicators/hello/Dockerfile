FROM python:2

RUN mkdir /src/

ADD ./communicator.py /src/
ADD ./settings_example.yml /src/

RUN pip install alexander_fw -U
CMD ["python", "/src/communicator.py", "run", "communicator", "--config", "/src/settings_example.yml"]
