from flask_wtf import FlaskForm
from flask import current_app, request as http_request


class ValidatedForm(FlaskForm):
    def perform_extra_validation(self, *args, **kwargs):
        """Performs any applicable extra validation. Must
        return True if the form is valid or False otherwise."""
        return True

    @property
    def data(self):
        _data = super().data
        _data.pop("csrf_token", None)
        return _data


class CacheableForm(ValidatedForm):
    def __init__(self, formdata=None, **kwargs):
        formdata = formdata or {}
        cached_data = current_app.form_cache.from_request(http_request)
        cached_data.update(formdata)
        super().__init__(cached_data, **kwargs)
