FROM nginx:1.17.4-alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY gunicorn_nginx.conf /etc/nginx/conf.d
