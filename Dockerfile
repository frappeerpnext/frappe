FROM ubuntu:14.04
RUN apt-get install git && \
git clone https://github.com/frappeerpnext/frappe
