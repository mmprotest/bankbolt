FROM python:3.11-slim

WORKDIR /app
COPY . /app
ENV PYTHONPATH=/app/src
ENV LICENSE_BYPASS=1
CMD ["python", "-m", "bank_normalizer.service.web"]
