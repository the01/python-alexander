FROM python:2

RUN mkdir /src/

ADD ./actor_manager.py /src/ 
ADD ./settings_example.yml /src/

RUN pip install alexander_fw
CMD ["python", "/src/actor_manager.py", "--debug", "--config", "/src/settings_example.yml"]
