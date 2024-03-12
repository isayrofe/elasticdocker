FROM python:3.12.2
ENV PYTHONUNBUFFERED=1

WORKDIR /app


COPY ./requirements.txt ./

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
        gcc \
        musl-dev \
        libpq-dev \
        # postgresql \
        python3-dev \
        libffi-dev \
        # libglvnd-dev \
        # libjpeg62-turbo-dev \
        libpng-dev \
        python3-setuptools \
        build-essential

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends gcc build-essential \
#     python3-dev python3-setuptools \
#     postgresql-client libpq-dev \
#     && rm -rf /var/lib/apt/lists/* \
#     && apt-get purge -y --auto-remove gcc build-essential

# Instalar dependencias
RUN pip3 install --upgrade pip \
    && pip3 install -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get purge -y --auto-remove gcc build-essential

COPY ./ ./

CMD ["sh", "entrypoint.sh"]