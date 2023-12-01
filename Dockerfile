FROM ubuntu:22.04
RUN apt-get install git && \
sudo apt-get update -y  && \
sudo apt-get upgrade -y
