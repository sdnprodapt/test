FROM dockerreg.cyanoptics.com/cyan/trusty-python:0.1.0-4

RUN pip install --upgrade pip==6.0.8

ADD bp2/hooks /bp2/hooks

WORKDIR /bp2/src/

ADD requirements.txt /bp2/src/
RUN pip install -i 'https://pypi.cyanoptics.com/simple/' -r requirements.txt

ADD . /bp2/src/
RUN pip install -e .
