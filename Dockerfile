FROM python:3.8.0b3-slim as base

RUN pip install --no-cache-dir --upgrade -U pip

FROM base as builder

RUN mkdir /install

WORKDIR /install

COPY /requirements.txt /requirements.txt

RUN pip install --prefix=/install -r /requirements.txt

FROM base

COPY --from=builder /install /usr/local

ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_19_10:$LD_LIBRARY_PATH

RUN apt-get update && apt-get install -y --no-install-recommends alien libaio1 wget && \
    wget https://download.oracle.com/otn_software/linux/instantclient/185000/oracle-instantclient18.5-basiclite-18.5.0.0.0-3.x86_64.rpm && \
    wget https://download.oracle.com/otn_software/linux/instantclient/185000/oracle-instantclient18.5-devel-18.5.0.0.0-3.x86_64.rpm && \
    alien -i oracle-instantclient18.5-basiclite-18.5.0.0.0-3.x86_64.rpm && \
    alien -i oracle-instantclient18.5-devel-18.5.0.0.0-3.x86_64.rpm
ENV LD_LIBRARY_PATH="/usr/lib/oracle/18.5/client64/lib:${LD_LIBRARY_PATH}"

RUN mkdir /src

COPY . /src

WORKDIR /src

ENV PYTHONBUFFERED 1
ENV FLASK_APP=/src/app.py
ENV FLASK_DEBUG=true
ENV FLASK_ENV=development