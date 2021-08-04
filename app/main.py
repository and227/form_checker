from fastapi import FastAPI, Depends, Body, status
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi.exceptions import HTTPException

from motor.motor_asyncio import AsyncIOMotorClient

from app.db.mongodb import get_database, connect_db, disconnect_db
from app.core.validators import get_type_by_validation
from app.core.config import settings

from os import path
import logging.config

import bson

log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.conf')
logging.config.fileConfig(log_file_path, disable_existing_loggers=False)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_event_handler("startup", connect_db)
app.add_event_handler("shutdown", disconnect_db)


@app.post('/add_form')
async def add_form(
    form_data = Body(None),
    db: AsyncIOMotorClient = Depends(get_database)
):
    collection = db[settings.FORM_DB_NAME][settings.FORM_DB_COLLECTION]
    await collection.insert_one(form_data.copy())

    return JSONResponse(status_code=status.HTTP_201_CREATED, content=form_data)


@app.get('/get_forms')
async def get_forms(
        db: AsyncIOMotorClient = Depends(get_database)
):
    collection = db[settings.FORM_DB_NAME][settings.FORM_DB_COLLECTION]
    cursor = collection.find({}, {'_id': 0})
    form_list = await cursor.to_list(length=128)

    return form_list


def check_query_fields(in_str):
    if in_str and type(in_str) == str and (in_str.count('=') == in_str.count('&') + 1):
        return True
    else:
        return False


async def find_form(form_collection, form_fields):
    list_field_keys = list(form_fields.keys())
    get_fields_pipeline = [
        {
            "$addFields": {
                "isSubset": {
                    "$setIsSubset": ["$fields", list_field_keys]
                }
            }
        }, 
        {
            "$match": {"isSubset": True }
        },
        {
            "$addFields": {
                "checkFields": {
                    "$setIntersection": ["$fields", list_field_keys]
                }
            }
        }
    ]

    cursor = form_collection.aggregate(get_fields_pipeline)
    ret_form = await cursor.to_list(length=None)
    if len(ret_form) > 0:
        match_fields = dict()
        for field in form_fields:
            if field in ret_form[0]['checkFields']:
                logger.info('key '+field)
                logger.info('value '+form_fields[field])
                match_fields.update({field: form_fields[field]})

        cursor = form_collection.find_one(match_fields)
    
        return ret_form

    return None

@app.post('/get_form')
async def get_form(
        query_string: str = Body(None),
        db: AsyncIOMotorClient = Depends(get_database)
):
    ret_form = None

    if check_query_fields(query_string):
        form_params = { param.split('=')[0]: param.split('=')[1] for param in query_string.split('&') }
        collection = db[settings.FORM_DB_NAME][settings.FORM_DB_COLLECTION]
        ret_form = await find_form(collection, form_params)

        if ret_form:
            return PlainTextResponse(content=ret_form[0]['name']) 
        else:
            ret_form_types = { param_key: get_type_by_validation(form_params[param_key]) for param_key in form_params }
            return JSONResponse(content=ret_form_types)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Set form fields')
