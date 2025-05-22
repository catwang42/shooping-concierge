# Use a slim Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Install Agent Framework
COPY google_genai_agents-0.0.2.dev20250304+733376416-py3-none-any.whl .
RUN pip install google_genai_agents-0.0.2.dev20250304+733376416-py3-none-any.whl

# Copy your app code
COPY . .

# Expose port 8080
EXPOSE 8080

# Run hypercorn
CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8080"]