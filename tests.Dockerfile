FROM python:3.6

RUN pip3 install fastapi pymongo pytest pytest-asyncio httpx python-dotenv uvicorn

# COPY ./tests/ /tests

WORKDIR /tests
CMD ["pytest", "test_forms.py"]