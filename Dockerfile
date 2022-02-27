# Base image
FROM python:3.9

COPY *.py /nowarddos/
COPY requirements.txt /nowarddos/

WORKDIR /nowarddos
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "attack.py"]