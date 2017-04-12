FROM artifactory.ciena.com/blueplanet/base-image-devops-toolkit:20170301

WORKDIR /bp2/src/

ARG pypi='https://artifactory.ciena.com/api/pypi/blueplanet-ubuntu-trusty-pypi/simple'

COPY .devops-toolkit /bp2/.devops-toolkit
COPY requirements.txt /bp2/src/
RUN pip install --find-links /bp2/.devops-toolkit -i $pypi -r requirements.txt

COPY . /bp2/src/
RUN pip install --find-links /bp2/.devops-toolkit -i $pypi -e .
