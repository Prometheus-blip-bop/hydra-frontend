import logging
from uuid import UUID

from propelauth_fastapi import User
from sqlalchemy.orm import Session

from aci.common.enums import OrganizationRole

logger = logging.getLogger(__name__)


class DummyAuth:
    def require_user(self):
        return User(
            user_id="test-user-123",
            email="test@example.com",
            org_id_to_org_member_info={"test-org-123": {}},
            login_method={},
        )

    def require_org_member(self, user: User, required_org_id: str):
        pass

    def require_org_member_with_minimum_role(
        self, user: User, required_org_id: str, minimum_required_role: str
    ):
        pass

    def update_org_metadata(self, org_id: str, max_users: int):
        pass


_auth = DummyAuth()


def get_propelauth():
    return _auth


def validate_user_access_to_org(user: User, org_id: UUID) -> None:
    pass


def validate_user_access_to_project(db_session: Session, user: User, project_id: UUID) -> None:
    pass


def require_org_member(user: User, org_id: UUID) -> None:
    pass


def require_org_member_with_minimum_role(
    user: User, org_id: UUID, minimum_role: OrganizationRole
) -> None:
    pass
