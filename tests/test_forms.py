from logging import Logger
import logging
import pytest
from httpx import AsyncClient

from pymongo import MongoClient
import json
import ast
from collections import OrderedDict
import os
import re


@pytest.fixture(scope='module')
def connect_mongodb():
    client = MongoClient(os.getenv('MONGODB_URL'))
    db = client[os.getenv('FORM_DB_NAME')]
    return db
    

@pytest.fixture(scope='module')
def fill_collection_test_data(connect_mongodb):
    db = connect_mongodb
    form1 = {
        "name": "Account form",
        "fields": ["username", "user_email", "user_phone"],
        "username": "some_username",
        "user_email": "some_email@gmail.com",
        "user_phone": "+71234567890"
    }

    form2 = {
        "name": "Order form",
        "fields": ["order_name", "order_description", "create_date", "complite_date"],
        "order_name": "order name",
        "order_description": "order description",
        "create_date": "31.07.2021",
        "complite_date": "01.08.2021"
    }

    form3 = {
        "name": "Task form",
        "fields": ["description", "start_date", "end_date"],
        "description": "test description",
        "start_date": "31.07.2021",
        "end_date": "01.08.2021"
    }

    db[os.getenv('FORM_DB_COLLECTION')].insert_many([form1, form2, form3])

    yield db

    db[os.getenv('FORM_DB_COLLECTION')].delete_many({})


@pytest.fixture(scope='module')
def get_test_queries():
    with open('queries.txt', 'r') as f:
        queries = list(filter(lambda line: not line.startswith('#') and not re.match(r'^\n$', line), f.readlines()))
    return queries


@pytest.mark.asyncio
async def test_queries(fill_collection_test_data, get_test_queries):
    db = fill_collection_test_data
    queries = get_test_queries
    async with AsyncClient() as ac:
        for query in queries:
            body, expect = query.split(';')
            print(query)
            expect = ast.literal_eval(expect)
            response = await ac.post("http://web_app:8000/get_form", content=body, headers={'Content-Type': "text/plain"})
            assert response.status_code == 200
            assert response.content.decode() == expect


@pytest.mark.asyncio
async def test_novalid_query(fill_collection_test_data):
    db = fill_collection_test_data
    async with AsyncClient() as ac:
        response = await ac.post("http://web_app:8000/get_form", content='some test string', headers={'Content-Type': "text/plain"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Set form fields'}


@pytest.mark.asyncio
async def test_nodata_query(fill_collection_test_data):
    db = fill_collection_test_data
    async with AsyncClient() as ac:
        response = await ac.post("http://web_app:8000/get_form", headers={'Content-Type': "text/plain"})
        assert response.status_code == 400
        assert response.json() == {'detail': 'Set form fields'}