FROM python:3.9-slim
# apt-get install libgdal-dev
RUN apt update && apt install -y libexpat1
RUN pip install requests osmium geopy
RUN pip install matplotlib