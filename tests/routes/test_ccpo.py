from flask import url_for

from atst.utils.localization import translate

from tests.factories import UserFactory


def test_ccpo_users(user_session, client):
    ccpo = UserFactory.create_ccpo()
    user_session(ccpo)
    response = client.get(url_for("ccpo.users"))
    assert ccpo.email in response.data.decode()


def test_submit_new_user(user_session, client):
    ccpo = UserFactory.create_ccpo()
    new_user = UserFactory.create()
    random_dod_id = "1234567890"
    user_session(ccpo)

    # give new_user CCPO permissions
    response = client.post(
        url_for("ccpo.submit_new_user"), data={"dod_id": new_user.dod_id}
    )
    assert new_user.email in response.data.decode()

    # give person with out ATAT account CCPO permissions
    response = client.post(
        url_for("ccpo.submit_new_user"), data={"dod_id": random_dod_id}
    )
    assert translate("ccpo.form.user_not_found_title") in response.data.decode()


def test_confirm_new_user(user_session, client):
    ccpo = UserFactory.create_ccpo()
    new_user = UserFactory.create()
    random_dod_id = "1234567890"
    user_session(ccpo)

    # give new_user CCPO permissions
    response = client.post(
        url_for("ccpo.confirm_new_user"),
        data={"dod_id": new_user.dod_id},
        follow_redirects=True,
    )
    assert new_user.dod_id in response.data.decode()

    # give person with out ATAT account CCPO permissions
    response = client.post(
        url_for("ccpo.confirm_new_user"),
        data={"dod_id": random_dod_id},
        follow_redirects=True,
    )
    assert random_dod_id not in response.data.decode()
