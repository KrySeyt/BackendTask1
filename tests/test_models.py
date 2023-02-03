from app import models


async def test_client_create(testing_database):
    tag = models.MailingTag("tag")
    testing_database.add(tag)
    await testing_database.commit()

    expected_result = models.Client(
        phone_number="+71111111111",
        phone_operator_code=900,
        tag=tag,
        timezone="Europe/Amsterdam"
    )

    result = await models.Client.create(
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
