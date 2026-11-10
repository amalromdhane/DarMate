from app.application.dto.dto import Actor
from app.application.interfaces.services import UnitOfWork
from app.core.exceptions import NotFoundError
from app.domain.entities import entities as e
from app.domain.repositories import ports


class Notifications:
    def __init__(self, repo: ports.NotificationRepository, uow: UnitOfWork) -> None:
        self.repo, self.uow = repo, uow

    def list(self, actor: Actor, unread_only: bool = False, limit: int = 50) -> tuple[list[e.Notification], int]:
        return self.repo.list_for_user(actor.id, unread_only, min(limit, 100)), self.repo.unread_count(actor.id)

    def mark_read(self, actor: Actor, notification_id: int) -> None:
        n = self.repo.get(notification_id)
        if n is None or n.user_id != actor.id:
            raise NotFoundError("Notification introuvable.")
        n.is_read = True
        self.repo.update(n)
        self.uow.commit()

    def mark_all_read(self, actor: Actor) -> None:
        self.repo.mark_all_read(actor.id)
        self.uow.commit()
