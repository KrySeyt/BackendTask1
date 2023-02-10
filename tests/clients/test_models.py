from src.mailings import models as mailings_models
from src.clients import models as clients_models


async def test_client_create(testing_database):
    tag = mailings_models.MailingTag("tag")
    testing_database.add(tag)
    await testing_database.commit()

    expected_result = clients_models.Client(
        phone_number="+71111111111",
        phone_operator_code=900,
        tag=tag,
        timezone="Europe/Amsterdam"
    )

    result = await clients_models.Client.create(
        db=testing_database,
        phone_number="+71111111111",
        phone_operator_code=900,
        tag_text="tag",
        timezone="Europe/Amsterdam"
    )

    assert result.tag.text == expected_result.tag.text
    assert result.phone_number == expected_result.phone_number
    assert result.phone_operator_code == expected_result.phone_operator_code
    assert result.timezone == expected_result.timezone
