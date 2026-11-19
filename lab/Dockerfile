ARG PHP_IMAGE=php:8.4.27-apache
FROM ${PHP_IMAGE}

COPY php-lab.ini /usr/local/etc/php/conf.d/zz-lab.ini
COPY apache-lab.conf /etc/apache2/conf-enabled/zz-lab.conf
COPY mpm-prefork.conf /etc/apache2/mods-available/mpm_prefork.conf
COPY www/ /var/www/html/

RUN mkdir -p /var/log \
	&& touch /var/log/php-error.log \
	&& chown www-data:www-data /var/log/php-error.log /var/www/html \
	&& chmod 644 /var/log/php-error.log \
	&& rm -f /var/www/html/index.html
