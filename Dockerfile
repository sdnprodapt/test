FROM artifactory.ciena.com/blueplanet/trusty-python:0.2.2-0

WORKDIR /bp2/src/

COPY requirements.txt /bp2/src/
RUN pip install -i 'https://artifactory.ciena.com/api/pypi/blueplanet-ubuntu-trusty-pypi/simple' -r requirements.txt

# lxml dependency
RUN apt-get update -y -q
RUN apt-get install -y -q libxslt-dev libxml2-dev libffi-dev libssl-dev openjdk-7-jre-headless

COPY . /bp2/src/
RUN pip install -e .
