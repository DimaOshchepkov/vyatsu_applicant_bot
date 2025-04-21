FROM python:3.13-slim AS compile-image

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip

# Final image
FROM python:3.13-slim
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=compile-image /opt/venv /opt/venv

WORKDIR /app

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
    pip install torch==2.6.0 --index-url https://download.pytorch.org/whl/cpu

COPY . .

RUN --mount=type=cache,mode=0755,target=/root/.cache/pip \
	pip install -e .

