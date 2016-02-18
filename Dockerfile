FROM python:2.7

WORKDIR /userapi
ADD requirements.txt /userapi/requirements.txt
RUN pip install -r requirements.txt

ADD . /userapi/
RUN python setup.py install

EXPOSE 8000
ENTRYPOINT ["/usr/local/bin/gunicorn", "-b", "0.0.0.0:8000", "userapi.api:APP"]
