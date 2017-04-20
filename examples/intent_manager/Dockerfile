FROM python:2

RUN mkdir /src/

ADD ./intent_manager.py /src/ 
ADD ./settings_example.yml /src/

RUN pip install alexander_fw
CMD ["python", "/src/intent_manager.py", "--debug", "--config", "/src/settings_example.yml"]
