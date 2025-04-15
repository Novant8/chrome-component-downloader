FROM python:3.13-alpine AS builder

WORKDIR /app

# Install Poetry
RUN pip install poetry \
    && poetry config virtualenvs.create false

# Transfer source code
COPY . .

# Build project
RUN poetry build

FROM python:3.13-alpine AS runner

ENV PYTHONUNBUFFERED=1

# Install project dependencies
RUN apk add --no-cache gcc python3-dev musl-dev linux-headers

RUN mkdir /app

WORKDIR /app

# Copy project files
COPY --from=builder /app/dist /app/dist

# Install package
RUN pip install dist/*.whl && rm -rf dist

ENTRYPOINT ["chrome-component-downloader"]