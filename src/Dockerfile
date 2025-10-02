FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim
LABEL authors="emiliocimino"

WORKDIR /home

COPY . .

RUN uv init
RUN uv add -r ./requirements.txt


CMD [".venv/bin/fastapi", "run", "server/app.py", "--port", "8010"]
