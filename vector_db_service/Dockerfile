# Build stage
FROM python:3.13-slim AS compile-image

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip

# Final image
FROM python:3.13-slim

COPY --from=compile-image /opt/venv /opt/venv

WORKDIR /app
ENV HOME=/app

RUN addgroup --system app && adduser --system --group app

COPY . .

RUN chown -R app:app $HOME
RUN chown -R app:app "/opt/venv/"

USER app

# RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install -e .




