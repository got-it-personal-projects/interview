FROM python:3.9.7-buster

ENV PYTHONUNBUFFERED=1
ENV INSTALL_PATH /blog-gotit
RUN mkdir -p $INSTALL_PATH

WORKDIR $INSTALL_PATH

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "app:create_app()"
