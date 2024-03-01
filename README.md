#Setup

- В терміналі: python -m venv venv
- venv/Scripts/activate
- pip install requirements.txt
- uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
- Go http://127.0.0.1:8000/docs