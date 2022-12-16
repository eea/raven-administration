FROM node:18.12.1-alpine as build-stage
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY ./ .
RUN npm run build 

FROM httpd as production-stage
RUN mkdir /app
COPY --from=build-stage /app/dist /app 
COPY ./httpd.conf /usr/local/apache2/conf/httpd.conf
COPY ./custom.conf /usr/local/apache2/conf/sites/custom.conf
EXPOSE 80
CMD ["httpd", "-D", "FOREGROUND"]