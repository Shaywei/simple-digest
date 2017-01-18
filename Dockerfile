# VERSION               0.0.1

FROM      ubuntu:14.04
MAINTAINER Shay Weiss <another.shay.weiss@gmail.com>

LABEL Description="This image is a simple message digest service"

RUN apt-get -qqy update

# Not required, but might be useful for local testing
RUN apt-get -qqy install curl

# Install huptime for watchdog deployment
# See: https://github.com/amscanne/huptime
RUN apt-get -qqy install build-essential
RUN apt-get -qqy install git
WORKDIR /tmp
RUN git clone https://github.com/amscanne/huptime
RUN cd huptime && make deb && dpkg -i huptime*.deb

# Copy script files
RUN mkdir /digest-flask-web-app
ADD digest-flask-web-app/ /digest-flask-web-app/
ADD digest-flask-web-app/digest.py /digest-flask-web-app/digest.py
ADD digest-flask-web-app/requirements.txt /digest-flask-web-app/requirements.txt

# Install Python dependencies
RUN apt-get -qqy install python-pip
RUN pip install --upgrade pip
WORKDIR /digest-flask-web-app
RUN pip install -r requirements.txt


# Run the app
EXPOSE 5000
ENTRYPOINT ["huptime", "--exec", "/digest-flask-web-app/digest.py", "-l", "/digest-flask-web-app/app.log", "-d", "/digest-flask-web-app/app.db"]
