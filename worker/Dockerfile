# Build upon this image "alpine" is a lightweight distro
FROM acleancoder/imagemagick-full:latest

RUN apt update; exit 0
RUN apt install -y python3-pip

# Copy requirements.txt
COPY ./requirements.txt /app/requirements.txt

# Install all the requirements
RUN pip3 install -r /app/requirements.txt

# Copy everthing from . to /app inside the 'box'
COPY . /app
WORKDIR /app

# How to run it when we start up the box?
CMD ["./thumbnail_worker.py"]
