# Pull official base image
FROM python:3.13-slim

# Meta-informação
LABEL maintainer="almanaque"
LABEL version="1.0"
LABEL description="Imagem Docker para aplicação Django"

# Allow overriding the container user/group IDs to match the host
ARG APP_UID=1000
ARG APP_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Create the app user with configurable UID/GID
RUN groupadd --system --gid "${APP_GID}" app \
    && useradd --system --uid "${APP_UID}" --gid app --home /home/app --create-home --shell /bin/bash app

# Create the appropriate directories
ARG options
ENV OPTIONS=$options
ENV HOME=/home/app
RUN mkdir -p $HOME/media
ENV UV_PROJECT_ENVIRONMENT=$HOME/.venv
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install image dependencies
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install -y --no-install-recommends \
    gettext \
    poppler-utils -y \
    libpango-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libpangocairo-1.0-0 \
    gcc \
    libc-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . .

ARG INSTALL_DEV=false
ENV INSTALL_DEV=${INSTALL_DEV}
ENV UV_LINK_MODE=copy

# Install dependencies with uv
RUN if [ "$INSTALL_DEV" = "true" ]; then \
    echo ">>> Modo desenvolvimento habilitado: instalando pacotes extras..." && \
    apt-get update && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/* && \
    \
    echo ">>> Configurando usuário app..." && \
    usermod -s /bin/bash app && \
    echo "app ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers && \
    \
    echo ">>> Instalando dependências em modo DEV..." && \
    uv sync --dev --python $(which python3) && \
    \
    echo ">>> Ativando virtualenv automático..." && \
    echo "source $UV_PROJECT_ENVIRONMENT/bin/activate" >> /home/app/.bashrc; \
    else \
    echo ">>> Modo produção: instalando dependências congeladas..." && \
    uv sync --frozen; \
    fi

# Ensure .venv/bin is on PATH
ENV PATH="$UV_PROJECT_ENVIRONMENT/bin:$PATH"

# Chown all the files to the app user
RUN chown -R app:app $HOME

# Change to the app user
USER app

CMD ["uv", "run", "gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--timeout", "90"]
