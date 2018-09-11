from tests.factories import (
    RequestFactory,
    UserFactory,
    RequestStatusEventFactory,
    RequestReviewFactory,
)
from atst.domain.requests import Requests, RequestStatus


def test_pending_financial_requires_mo_action():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.PENDING_FINANCIAL_VERIFICATION)

    assert request.action_required_by == "mission_owner"


def test_pending_ccpo_approval_requires_ccpo():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.PENDING_CCPO_APPROVAL)

    assert request.action_required_by == "ccpo"


def test_request_has_creator():
    user = UserFactory.create()
    request = RequestFactory.create(creator=user)

    assert request.creator == user


def test_request_status_started_displayname():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.STARTED)

    assert request.status_displayname == "Started"


def test_request_status_pending_financial_displayname():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.PENDING_FINANCIAL_VERIFICATION)

    assert request.status_displayname == "Pending Financial Verification"


def test_request_status_pending_ccpo_displayname():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.PENDING_CCPO_APPROVAL)

    assert request.status_displayname == "Pending CCPO Approval"


def test_request_status_pending_approved_displayname():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.APPROVED)

    assert request.status_displayname == "Approved"


def test_request_status_pending_expired_displayname():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.EXPIRED)

    assert request.status_displayname == "Expired"


def test_request_status_pending_deleted_displayname():
    request = RequestFactory.create()
    request = Requests.set_status(request, RequestStatus.DELETED)

    assert request.status_displayname == "Deleted"


def test_annual_spend():
    request = RequestFactory.create()
    monthly = request.body.get("details_of_use").get("estimated_monthly_spend")
    assert request.annual_spend == monthly * 12


def test_reviews():
    request = RequestFactory.create()
    ccpo = UserFactory.from_atat_role("ccpo")
    request.status_events = [
        RequestStatusEventFactory.create(
            revision=request.latest_revision,
            review=RequestReviewFactory.create(reviewer=ccpo),
        ),
        RequestStatusEventFactory.create(
            revision=request.latest_revision,
            review=RequestReviewFactory.create(reviewer=ccpo),
        ),
        RequestStatusEventFactory.create(revision=request.latest_revision),
    ]
    assert len(request.reviews) == 2
