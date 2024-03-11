# Python Image
FROM python:3.10.11

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

# Expose the port on which Streamlit will run
EXPOSE 8501

# Command to launch the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
