FROM ubuntu:20.04

RUN apt-get update \
 && apt-get install -y sudo apt-transport-https ca-certificates curl python python3-pip bc\
 && sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg \
 && echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list \
 && apt-get update \
 && apt-get install kubectl \
 && sudo apt-get clean

RUN adduser --disabled-password --gecos '' ubuntu \
  && adduser ubuntu sudo \
  && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu

WORKDIR /app

COPY fixture/* ./
COPY scaler.sh ./

RUN pip3 install -r requirements.txt

ENTRYPOINT ["/bin/bash", "scaler.sh"]