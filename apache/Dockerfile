FROM httpd:latest
RUN mkdir -p /usr/local/apache2/conf/sites/
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./custom.conf /usr/local/apache2/conf/sites/custom.conf
EXPOSE 80
CMD ["httpd", "-D", "FOREGROUND"]