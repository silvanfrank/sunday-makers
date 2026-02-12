# Dockerfile
# Base image: Lightweight Python 3.11 (Slim) for efficiency
FROM python:3.11-slim

# Set working directory in container
WORKDIR /app

# Install system dependencies (none strictly needed for this logic, but good practice to have basics)
# If we need pdf generation later, we might need other libaries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# We create a requirements.txt on the fly here to keep it simple self-contained, 
# or we could COPY one. For the Investment Co-Pilot, the deps are minimal.
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire execution directory into /app/execution
COPY execution/ /app/execution/

# Copy the directives into /app/directives (for context/reference if needed by API)
COPY directives/ /app/directives/

# Create .tmp directory for intermediate files
RUN mkdir -p .tmp

# Expose port (if we wrap in FastAPI later)
EXPOSE 8000

# Default command: Run the FastAPI wrapper (which we will build next)
CMD ["uvicorn", "execution.api:app", "--host", "0.0.0.0", "--port", "8000"]
