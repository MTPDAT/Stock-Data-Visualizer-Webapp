FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies needed for matplotlib
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY api_handler.py .
COPY visualizer.py .
COPY stocks.csv .

# Copy templates and static folders
COPY templates/ templates/
COPY static/ static/

# Expose Flask port
EXPOSE 5005

# Set environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
# Matplotlib must use non-interactive backend in a container (no display)
ENV MPLBACKEND=Agg

# Run the app
CMD ["python", "app.py"]