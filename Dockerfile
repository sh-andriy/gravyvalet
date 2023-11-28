# Use the official Python image as the base image
FROM python:3.12

# System Dependencies:
RUN apt-get update && apt-get install -y libpq-dev

WORKDIR /code
COPY requirements/ /code/requirements/

# Python dependencies:
RUN pip3 install --no-cache-dir -r requirements/requirements.txt

COPY . /code/

EXPOSE 8000

# Start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]