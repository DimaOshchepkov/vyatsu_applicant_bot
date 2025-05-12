FROM python:3.13-slim AS compile-image

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip

RUN pip install --no-cache-dir uv

# Final image
FROM python:3.13-slim
ENV PATH="/opt/venv/bin:$PATH"

COPY --from=compile-image /opt/venv /opt/venv

WORKDIR /app

ARG REQUIREMENTS=requirements.txt
COPY ${REQUIREMENTS} ${REQUIREMENTS}

RUN --mount=type=cache,mode=0755,target=/root/.cache/uv \
    uv pip install -r ${REQUIREMENTS}

COPY . .

RUN --mount=type=cache,mode=0755,target=/root/.cache/uv \
    uv pip install -e .


