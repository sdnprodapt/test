FROM cyan/rajuniper-base

# lxml dependency
RUN apt-get update -y -q && \
    apt-get install -y -q libxslt-dev libxml2-dev libffi-dev libssl-dev openjdk-7-jre-headless

RUN pip install -i 'https://artifactory.ciena.com/api/pypi/blueplanet-pypi/simple' lxml

WORKDIR /bp2/src/

EXPOSE 22
EXPOSE 8080

ENV NBI_rajunipersim_port=22
ENV NBI_rajunipersim_publish=True
ENV NBI_rasim_port=22
ENV NBI_rasim_typeGroup=Juniper
ENV NBI_rasim_username=admin
ENV NBI_rasim_password=admin
ENV NBI_rasim_publish=True
