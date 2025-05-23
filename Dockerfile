ARG PYTHON_VERSION=3.12-slim-bullseye
FROM python:${PYTHON_VERSION}

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --upgrade pip

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y \
    libpq-dev \
    libjpeg-dev \
    libcairo2 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app
WORKDIR /app
COPY requirements.txt /tmp/requirements.txt
COPY ./backend /app

RUN pip install -r /tmp/requirements.txt

ARG DJANGO_SECRET_KEY
ENV DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY

ARG DJANGO_DEBUG
ENV DJANGO_DEBUG=$DJANGO_DEBUG

ARG CONN_MAX_AGE
ENV CONN_MAX_AGE=$CONN_MAX_AGE

ARG EMAIL_HOST
ENV EMAIL_HOST=$EMAIL_HOST

ARG EMAIL_PORT
ENV EMAIL_PORT=$EMAIL_PORT

ARG EMAIL_HOST_USER
ENV EMAIL_HOST_USER=$EMAIL_HOST_USER

ARG EMAIL_HOST_PASSWORD
ENV EMAIL_HOST_PASSWORD=$EMAIL_HOST_PASSWORD

ARG EMAIL_USE_TLS
ENV EMAIL_USE_TLS=$EMAIL_USE_TLS

ARG EMAIL_USE_SSL
ENV EMAIL_USE_SSL=$EMAIL_USE_SSL

ARG ADMIN_EMAIL
ENV ADMIN_EMAIL=$ADMIN_EMAIL

ARG ADMIN_USERNAME
ENV ADMIN_USERNAME=$ADMIN_USERNAME

ARG DEFAULT_FROM_EMAIL
ENV DEFAULT_FROM_EMAIL=$DEFAULT_FROM_EMAIL

ARG GOOGLE_OAUTH_CLIENT_ID
ENV GOOGLE_OAUTH_CLIENT_ID=$GOOGLE_OAUTH_CLIENT_ID

ARG GOOGLE_OAUTH_CLIENT_SECRET
ENV GOOGLE_OAUTH_CLIENT_SECRET=$GOOGLE_OAUTH_CLIENT_SECRET

ARG GOOGLE_OAUTH_CALLBACK_URL
ENV GOOGLE_OAUTH_CALLBACK_URL=$GOOGLE_OAUTH_CALLBACK_URL

ARG CLOUDINARY_CLOUD_NAME
ENV CLOUDINARY_CLOUD_NAME=$CLOUDINARY_CLOUD_NAME

ARG CLOUDINARY_API_KEY
ENV CLOUDINARY_API_KEY=$CLOUDINARY_API_KEY

ARG CLOUDINARY_API_SECRET
ENV CLOUDINARY_API_SECRET=$CLOUDINARY_API_SECRET

ARG CLOUDINARY_RESOURCE_TYPE
ENV CLOUDINARY_RESOURCE_TYPE=$CLOUDINARY_RESOURCE_TYPE

ARG DEFAULT_FILE_STORAGE
ENV DEFAULT_FILE_STORAGE=$DEFAULT_FILE_STORAGE

ARG PROJ_NAME="backend"

RUN printf "#!/bin/bash\n" > ./paracord_runner.sh && \
    printf "RUN_PORT=\"\${PORT:-8000}\"\n" >> ./paracord_runner.sh && \
    printf "python manage.py migrate --no-input\n" >> ./paracord_runner.sh && \
    printf "python manage.py collectstatic --no-input\n" >> ./paracord_runner.sh && \
    printf "python manage.py create_groups\n" >> ./paracord_runner.sh && \
    printf "gunicorn ${PROJ_NAME}.wsgi:application --bind \"[::]:\$RUN_PORT\"\n" >> ./paracord_runner.sh
    
RUN chmod +x paracord_runner.sh
RUN apt-get remove --purge -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

CMD ./paracord_runner.sh