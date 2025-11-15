FROM python:3.10-slim 
WORKDIR /app 
COPY . . 
RUN pip install torch scikit-learn pandas 
CMD ["python", "agent/agent_runner.py"] 
