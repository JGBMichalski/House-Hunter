FROM ubuntu:focal

ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \ 
    python3 \
    python3-pip \ 
    wget \ 
    git \ 
    cron

# Install python dependencies
RUN pip install requests bs4 pyyaml

# Copy the setup python script to /usr/sbin
COPY HouseHunter/* /House-Hunter/HouseHunter/
COPY docker.py /House-Hunter
COPY hunter.py /House-Hunter
COPY config.yaml /House-Hunter
COPY ads.json /House-Hunter
COPY VERSION /House-Hunter

# Change the directory to /House-Hunter
WORKDIR /House-Hunter

# Setup HouseHunter if it is not already setup and execute HouseHunter once every 2 minutes using the docker config.yaml
CMD python3 docker.py && python3 hunter.py --conf /config/config.yaml --ads /config/ads.json --interval 120