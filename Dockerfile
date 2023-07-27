FROM python:3-alpine3.10
RUN apk add build-base
WORKDIR /app
COPY . /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD export FLASK_APP=app && export FLASK_DEBUG=TRUE && python app.py