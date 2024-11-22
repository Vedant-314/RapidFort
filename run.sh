#!/bin/bash

# Build the Docker image
docker build -t rapidfort .

# Run the container
docker run -p 5000:5000 rapidfort
