FROM dockerreg.cyanoptics.com/cyan/trusty-python:0.2.2-0

RUN ssh-keygen -t rsa -f /root/.ssh/id_rsa -q -N "" && \
    git config --global user.email "bprajuniperng@cyaninc.com" && \
    git config --global user.name "bprajuniperng"

WORKDIR /bp2/src/

ADD requirements.txt /bp2/src/
RUN pip install -i 'https://artifactory.ciena.com/api/pypi/blueplanet-pypi/simple' -r requirements.txt

ADD bp2/hooks /bp2/hooks
RUN ln -s /bp2/hooks/southbound-update /usr/local/bin/southbound-update

ADD . /bp2/src/
RUN pip install -e .
