FROM alpine:latest
MAINTAINER Yannis Storrer "yannis.storrer@web.de"
RUN apk update && apk upgrade && apk add --update-cache python3 py-pip
COPY . /server
WORKDIR /server
RUN pwd && ls
RUN pip install --ignore-installed pipenv
RUN pipenv install --system --deploy
ENTRYPOINT ["python3"]
CMD [ "app.py" ]
