FROM dockerreg.cyanoptics.com/cyan/trusty-python:0.1.0-4

RUN pip install --upgrade pip==6.0.8

RUN apt-get install -y -q libxslt1.1

WORKDIR /bp2/src/

ADD requirements.txt /bp2/src/
RUN pip install -i 'https://pypi.cyanoptics.com/simple/' -r requirements.txt

ADD bp2/hooks /bp2/hooks
RUN ln -s /bp2/hooks/southbound-update /usr/local/bin/southbound-update

ADD . /bp2/src/
RUN pip install -e .
