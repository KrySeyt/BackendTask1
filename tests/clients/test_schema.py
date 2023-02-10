import pydantic

from src.clients import schema

import pytest


class TestClientBase:
    async def test_timezone_exists_validator(self):
        schema.ClientBase(
            phone_number="+79009999999",
            phone_operator_code=900,
            timezone="Europe/Amsterdam"
        )

        with pytest.raises(pydantic.ValidationError):
            schema.ClientBase(
                phone_number="+79009999999",
                phone_operator_code=900,
                timezone="Doesn't exists"
            )

    async def test_phone_number_correct_validator(self):
        schema.ClientBase(
            phone_number="+79009999999",
            phone_operator_code=900,
            timezone="Europe/Amsterdam"
        )

        with pytest.raises(pydantic.ValidationError):
            schema.ClientBase(
                phone_number="+80000000000",
                phone_operator_code=900,
                timezone="Doesn't exists"
            )
