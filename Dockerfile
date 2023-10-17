FROM python:3.10

COPY requirements_prod.txt /usr/share/app/requirements.txt
RUN pip install -r /usr/share/app/requirements.txt

COPY app /usr/share/app

ENV PYTHONPATH "${PYTHONPATH}:/usr/share/app"

WORKDIR /usr/share/app/database
