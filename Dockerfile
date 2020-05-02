FROM python:3.8.2-alpine3.11
WORKDIR /app
RUN apk add gcc postgresql-dev musl-dev
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD ipamd /app/ipamd
ADD migrations /app/migrations
ADD wsgi.py /app/
ADD entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh
CMD ["/app/entrypoint.sh"]
