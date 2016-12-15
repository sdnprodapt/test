FROM artifactory.ciena.com/blueplanet/trusty-python:0.2.2-0

WORKDIR /bp2/src/

COPY requirements.txt /bp2/src/
RUN pip install -i 'https://artifactory.ciena.com/api/pypi/blueplanet-ubuntu-trusty-pypi/simple' -r requirements.txt

COPY . /bp2/src/
RUN pip install -e .
