FROM debian:wheezy
MAINTAINER BeneDicere
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install wget python python-pip -y && \
   apt-get clean autoclean && apt-get autoremove && \
   rm -rf /var/lib/{apt,dpkg,cache,log}
RUN mkdir /app
WORKDIR /app
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/
ENV LC_CTYPE  en_US.utf-8
WORKDIR /app/
CMD /app/run.py --config config.ini