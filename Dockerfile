FROM python:3.10-slim-buster

# copy files
COPY . /opera
WORKDIR /opera

# install requirements
RUN apt-get update \
    && apt-get install -y git-all \
    && pip install --upgrade pip wheel \
    && pip install -r requirements.txt \
    && pip install .

ENTRYPOINT ["opera", "--version", "/dev/null"]
