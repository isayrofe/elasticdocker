FROM python:latest
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && \
    apt-get install -y \
        gcc \
        musl-dev \
        libpq-dev \
        python3-dev \
        libffi-dev \
        libglvnd-dev \
        libjpeg62-turbo-dev \
        libpng-dev \
        build-essential

# Actualizar pip
RUN pip3 install --upgrade pip


COPY ./requirements.txt ./

RUN pip3 install -r requirements.txt

COPY ./ ./

CMD ["sh", "entrypoint.sh"]