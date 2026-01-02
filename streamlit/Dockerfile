FROM python:3.11-slim

WORKDIR /app

RUN pip install streamlit requests

COPY app.py .

CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]