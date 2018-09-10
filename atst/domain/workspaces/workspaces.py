from sqlalchemy.orm.exc import NoResultFound

from atst.database import db
from atst.models.workspace import Workspace
from atst.models.workspace_role import WorkspaceRole
from atst.domain.exceptions import NotFoundError
from atst.domain.roles import Roles
from atst.domain.authz import Authorization
from atst.models.permissions import Permissions
from atst.domain.users import Users
from atst.domain.workspace_users import WorkspaceUsers
from .scopes import ScopedWorkspace


class Workspaces(object):
    @classmethod
    def create(cls, request, name=None):
        name = name or request.id
        workspace = Workspace(request=request, name=name)
        Workspaces._create_workspace_role(request.creator, workspace, "owner")

        db.session.add(workspace)
        db.session.commit()

        return workspace

    @classmethod
    def get(cls, user, workspace_id):
        workspace = Workspaces._get(workspace_id)
        Authorization.check_workspace_permission(
            user, workspace, Permissions.VIEW_WORKSPACE, "get workspace"
        )

        return ScopedWorkspace(user, workspace)

    @classmethod
    def get_for_update(cls, user, workspace_id):
        workspace = Workspaces._get(workspace_id)
        Authorization.check_workspace_permission(
            user, workspace, Permissions.ADD_APPLICATION_IN_WORKSPACE, "add project"
        )

        return workspace

    @classmethod
    def get_by_request(cls, request):
        try:
            workspace = db.session.query(Workspace).filter_by(request=request).one()
        except NoResultFound:
            raise NotFoundError("workspace")

        return workspace

    @classmethod
    def get_with_members(cls, user, workspace_id):
        workspace = Workspaces._get(workspace_id)
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.VIEW_WORKSPACE_MEMBERS,
            "view workspace members",
        )

        return workspace

    @classmethod
    def get_many(cls, user):
        workspaces = (
            db.session.query(Workspace)
            .join(WorkspaceRole)
            .filter(WorkspaceRole.user == user)
            .all()
        )
        return workspaces

    @classmethod
    def create_member(cls, user, workspace, data):
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            "create workspace member",
        )

        new_user = Users.get_or_create_by_dod_id(
            data["dod_id"],
            first_name=data["first_name"],
            last_name=data["last_name"],
            email=data["email"],
        )
        return Workspaces.add_member(workspace, new_user, data["workspace_role"])

    @classmethod
    def add_member(cls, workspace, member, role_name):
        workspace_user = WorkspaceUsers.add(member, workspace.id, role_name)
        return workspace_user

    @classmethod
    def update_member(cls, user, workspace, member, role_name):
        Authorization.check_workspace_permission(
            user,
            workspace,
            Permissions.ASSIGN_AND_UNASSIGN_ATAT_ROLE,
            "edit workspace member",
        )

        return WorkspaceUsers.update_role(member, workspace.id, role_name)

    @classmethod
    def _create_workspace_role(cls, user, workspace, role_name):
        role = Roles.get(role_name)
        workspace_role = WorkspaceRole(user=user, role=role, workspace=workspace)
        db.session.add(workspace_role)
        return workspace_role

    @classmethod
    def _get(cls, workspace_id):
        try:
            workspace = db.session.query(Workspace).filter_by(id=workspace_id).one()
        except NoResultFound:
            raise NotFoundError("workspace")

        return workspace
