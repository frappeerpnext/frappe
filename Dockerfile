FROM ubuntu:22.04
RUN adduser erpuser && \
usermod -aG sudo erpuser && \
sudo apt-get update -y && \
sudo apt-get upgrade -y
