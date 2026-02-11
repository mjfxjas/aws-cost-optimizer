FROM python:3.12-slim

LABEL org.opencontainers.image.source="https://github.com/mjfxjas/aws-cost-optimizer"
LABEL org.opencontainers.image.description="AWS cost optimization recommendations and automation"
LABEL org.opencontainers.image.licenses="MIT"

WORKDIR /app

# Install aws-cost-optimizer from PyPI
RUN pip install --no-cache-dir aws-cost-optimizer

# Create non-root user
RUN useradd -m -u 1000 optimizer && chown -R optimizer:optimizer /app
USER optimizer

ENTRYPOINT ["aws-cost-optimizer"]
CMD ["--help"]
