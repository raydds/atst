from flask import Blueprint, request as http_request, render_template, g, redirect, url_for

from atst.domain.task_orders import TaskOrders
from atst.domain.workspaces import Workspaces
import atst.forms.task_order as task_order_form

task_orders_bp = Blueprint("task_orders", __name__)


TASK_ORDER_SECTIONS = [
    {
        "section": "app_info",
        "title": "What You're Building",
        "template": "task_orders/new/app_info.html",
        "form": task_order_form.AppInfoForm,
    },
    {
        "section": "funding",
        "title": "Funding",
        "template": "task_orders/new/funding.html",
        "form": task_order_form.FundingForm,
    },
    {
        "section": "oversight",
        "title": "Oversight",
        "template": "task_orders/new/oversight.html",
        "form": task_order_form.OversightForm,
    },
    {
        "section": "review",
        "title": "Review & Download",
        "template": "task_orders/new/review.html",
        "form": task_order_form.ReviewForm,
    },
]


class ShowTaskOrderWorkflow:
    def __init__(self, screen=1, task_order_id=None):
        self.screen = screen
        self.task_order_id = task_order_id
        self._section = TASK_ORDER_SECTIONS[screen - 1]
        self._task_order = None
        self._form = None

    @property
    def task_order(self):
        if not self._task_order and self.task_order_id:
            self._task_order = TaskOrders.get(self.task_order_id)

        return self._task_order

    @property
    def form(self):
        if self._form:
            pass
        elif self.task_order:
            self._form = self._section["form"](data=self.task_order.to_dictionary())
        else:
            self._form = self._section["form"]()

        return self._form

    @property
    def template(self):
        return self._section["template"]


class UpdateTaskOrderWorkflow(ShowTaskOrderWorkflow):
    def __init__(self, form_data, user, screen=1, task_order_id=None):
        self.form_data = form_data
        self.user = user
        self.screen = screen
        self.task_order_id = task_order_id
        self._task_order = None
        self._section = TASK_ORDER_SECTIONS[screen - 1]

    @property
    def form(self):
        return self._section["form"](self.form_data)

    def validate(self):
        return self.form.validate()

    def update(self):
        if self.task_order:
            TaskOrders.update(self.task_order, **self.form.data)
        else:
            ws = Workspaces.create(self.user, self.form.portfolio_name.data)
            to_data = self.form.data.copy()
            to_data.pop("portfolio_name")
            self._task_order = TaskOrders.create(workspace=ws, creator=self.user)
            TaskOrders.update(self.task_order, **to_data)

        return self.task_order


@task_orders_bp.route("/task_order/new/<int:screen>")
@task_orders_bp.route("/task_order/new/<int:screen>/<task_order_id>")
def new(screen, task_order_id=None):
    workflow = ShowTaskOrderWorkflow(screen, task_order_id)
    return render_template(
        workflow.template,
        current=screen,
        task_order_id=task_order_id,
        screens=TASK_ORDER_SECTIONS,
        form=workflow.form,
    )


@task_orders_bp.route("/task_order/new/<int:screen>", methods=["POST"])
@task_orders_bp.route("/task_order/new/<int:screen>/<task_order_id>", methods=["POST"])
def update(screen, task_order_id=None):
    workflow = UpdateTaskOrderWorkflow(
        http_request.form, g.current_user, screen, task_order_id
    )

    if workflow.validate():
        workflow.update()
        return redirect(url_for("task_orders.new", screen=screen+1, task_order_id=workflow.task_order.id))
    else:
        return render_template(
            workflow.template,
            current=screen,
            task_order_id=task_order_id,
            screens=TASK_ORDER_SECTIONS,
            form=workflow.form,
        )
