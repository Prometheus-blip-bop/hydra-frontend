FROM python:3.12
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /workdir

COPY ./backend/pyproject.toml ./backend/uv.lock /workdir/
RUN uv sync --no-dev --no-install-project

ENV PATH="/workdir/.venv/bin:$PATH"
ENV PYTHONPATH=/workdir

COPY ./backend/apps /workdir/apps
COPY ./backend/aci/server /workdir/aci/server
COPY ./backend/aci/common /workdir/aci/common
COPY ./backend/aci/__init__.py /workdir/aci/__init__.py
COPY ./backend/alembic.ini /workdir/alembic.ini
COPY ./backend/aci/alembic /workdir/aci/alembic

# remove unecessary or sensitive files (.env files are skipped by default specified in .dockerignore)
RUN rm -rf /workdir/aci/server/tests

COPY ./backend/seed_hf.py /workdir/seed_hf.py

CMD sh -c "uv run alembic upgrade head && uv run python seed_hf.py && uvicorn aci.server.main:app --proxy-headers --forwarded-allow-ips=* --host 0.0.0.0 --port 7860 --no-access-log"
