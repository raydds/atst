from wtforms.fields import StringField
from wtforms.validators import Length

from .forms import CacheableForm
from atst.utils.localization import translate


class PortfolioForm(CacheableForm):
    name = StringField(
        translate("forms.portfolio.name_label"),
        validators=[
            Length(
                min=4,
                max=100,
                message=translate("forms.portfolio.name_length_validation_message"),
            )
        ],
    )