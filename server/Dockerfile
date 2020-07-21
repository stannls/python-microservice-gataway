FROM alpine:latest
MAINTAINER Yannis Storrer "yannis.storrer@web.de"
RUN apk update && apk upgrade && apk add --update python3 py-pip
COPY requirements.txt /server/requirements.txt
WORKDIR /server
RUN python3 -m pip install -r requirements.txt
COPY . /server
ENTRYPOINT [ "python3" ]
CMD [ "app.py" ]