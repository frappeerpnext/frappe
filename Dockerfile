FROM ubuntu:22.04
RUN apt-get update && \ 
apt-get install git && \
git clone https://github.com/frappeerpnext/frappe
