# Base image
FROM python:3.11-slim-buster

RUN apt-get update && apt-get install curl -y

# Set working directory
WORKDIR /

# Copy requirements.txt to container and install dependencies
COPY requirements.txt .
RUN pip3 install -r requirements.txt

USER root

# RUN apt-get update
# RUN apt-get install unixodbc-dev -y
# RUN apt-get install curl -y \
#     && apt-get install gnupg2 -y 

# RUN pip3 install --upgrade openai \
#     && pip3 install --upgrade pyodbc

# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
# RUN apt-get update && ACCEPT_EULA=Y apt-get install -y msodbcsql17


# Copy the Fast app to container
COPY . .

# USER root

# # Expose port 5000
# EXPOSE 5005

# Start Flask app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9001"]