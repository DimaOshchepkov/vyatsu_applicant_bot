FROM python:3.13-slim AS compile-image

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip

# Final image
FROM python:3.13-slim
ENV PATH="/opt/venv/bin:$PATH"
ARG EXTRA_GROUP=bot

COPY --from=compile-image /opt/venv /opt/venv

WORKDIR /app

COPY . .

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
	pip install -e ".[${EXTRA_GROUP}]"

