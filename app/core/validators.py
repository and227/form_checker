from pydantic import EmailStr
from typing import Optional
import datetime
import re


def validate_phone(value):
    if re.match(r'^\+7\d{10}$', value.replace(' ', '')):
        return value
    else:
        raise ValueError("value is not a valid phone number")


def validate_date(value):
    for form in ('%d.%m.%Y', '%Y-%m-%d'):
        try:
            datetime.datetime.strptime(value, form)
            return value
        except ValueError:
            pass

    raise ValueError('value in not a valid date')


def get_type_by_validation(value):
    validator_type = (
        (validate_phone, 'phone'),
        (validate_date, 'date'),
        (EmailStr.validate, 'email')
    )
    for validator_func, ret_type in validator_type:
        try:
            validator_func(value)
            return ret_type
        except ValueError:
            pass
    return 'text'
