# Use the official Python image as the base image
FROM python:3.12 as gv-base

# System Dependencies:
RUN apt-get update && apt-get install -y libpq-dev

COPY . /code/
WORKDIR /code
# END gv-base

# BEGIN gv-local
FROM gv-base as gv-local
# install dev and non-dev dependencies:
RUN pip3 install --no-cache-dir -r requirements/dev-requirements.txt
# Start the Django development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8004"]
# END gv-local

# BEGIN gv-deploy
FROM gv-base as gv-deploy
# install non-dev and release-only dependencies:
RUN pip3 install --no-cache-dir -r requirements/release.txt
# collect static files into a single directory:
RUN python manage.py collectstatic --noinput
# note: no CMD in gv-deploy -- depends on deployment
# END gv-deploy
