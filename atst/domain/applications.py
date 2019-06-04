from sqlalchemy.orm.exc import NoResultFound

from . import BaseDomainClass
from atst.database import db
from atst.domain.application_roles import ApplicationRoles
from atst.domain.environment_roles import EnvironmentRoles
from atst.domain.environments import Environments
from atst.domain.exceptions import NotFoundError
from atst.domain.invitations import ApplicationInvitations
from atst.domain.users import Users
from atst.models import (
    Application,
    ApplicationRole,
    ApplicationRoleStatus,
    EnvironmentRole,
)
from atst.utils import first_or_none


class Applications(BaseDomainClass):
    model = Application
    resource_name = "application"

    @classmethod
    def create(cls, portfolio, name, description, environment_names):
        application = Application(
            portfolio=portfolio, name=name, description=description
        )
        db.session.add(application)

        Environments.create_many(application, environment_names)

        db.session.commit()
        return application

    @classmethod
    def for_user(self, user, portfolio):
        return (
            db.session.query(Application)
            .join(ApplicationRole)
            .filter(Application.portfolio_id == portfolio.id)
            .filter(ApplicationRole.application_id == Application.id)
            .filter(ApplicationRole.user_id == user.id)
            .filter(ApplicationRole.status == ApplicationRoleStatus.ACTIVE)
            .all()
        )

    @classmethod
    def get_all(cls, portfolio):
        try:
            applications = (
                db.session.query(Application).filter_by(portfolio_id=portfolio.id).all()
            )
        except NoResultFound:
            raise NotFoundError("applications")

        return applications

    @classmethod
    def update(cls, application, new_data):
        if "name" in new_data:
            application.name = new_data["name"]
        if "description" in new_data:
            application.description = new_data["description"]

        db.session.add(application)
        db.session.commit()

        return application

    @classmethod
    def delete(cls, application):
        for env in application.environments:
            Environments.delete(env)

        application.deleted = True

        for role in application.roles:
            role.deleted = True
            db.session.add(role)

        db.session.add(application)
        db.session.commit()

    @classmethod
    def create_member(
        cls, application, user_data, permission_sets=None, environment_roles_data=None
    ):
        permission_sets = [] if permission_sets is None else permission_sets
        environment_roles_data = (
            [] if environment_roles_data is None else environment_roles_data
        )

        user = Users.get_or_create_by_dod_id(
            user_data["dod_id"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            phone_number=user_data.get("phone_number"),
            email=user_data["email"],
        )

        application_role = ApplicationRoles.create(user, application, permission_sets)

        for env_role_data in environment_roles_data:
            role = env_role_data.get("role")
            if role:
                environment = Environments.get(env_role_data.get("environment_id"))
                Environments.add_member(
                    environment, application_role, env_role_data.get("role")
                )

        return application_role

    @classmethod
    def invite(
        cls,
        application,
        inviter,
        user_data,
        permission_sets_names=None,
        environment_roles_data=None,
    ):
        permission_sets_names = permission_sets_names or []
        permission_sets = ApplicationRoles._permission_sets_for_names(
            permission_sets_names
        )
        app_role = ApplicationRole(
            application=application, permission_sets=permission_sets
        )

        db.session.add(app_role)

        for env_role_data in environment_roles_data:
            env_role_name = env_role_data.get("role")
            environment_id = env_role_data.get("environment_id")
            if env_role_name is not None:
                # pylint: disable=cell-var-from-loop
                environment = first_or_none(
                    lambda e: str(e.id) == str(environment_id), application.environments
                )
                if environment is None:
                    raise NotFoundError("environment")
                else:
                    env_role = EnvironmentRole(
                        application_role=app_role,
                        environment=environment,
                        role=env_role_name,
                    )
                    db.session.add(env_role)

        invitation = ApplicationInvitations.create(
            inviter=inviter, role=app_role, member_data=user_data
        )
        db.session.add(invitation)

        db.session.commit()

        return invitation

    @classmethod
    def remove_member(cls, application, user_id):
        application_role = ApplicationRoles.get(
            user_id=user_id, application_id=application.id
        )

        application_role.status = ApplicationRoleStatus.DISABLED
        application_role.deleted = True

        for env in application.environments:
            EnvironmentRoles.delete(
                application_role_id=application_role.id, environment_id=env.id
            )

        db.session.add(application_role)
        db.session.commit()
