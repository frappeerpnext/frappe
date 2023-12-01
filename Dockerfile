FROM ubuntu:22.04
RUN adduser erpuser && \
usermod -aG sudo erpuser
