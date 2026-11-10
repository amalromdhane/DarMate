"""Conversion des DTO/entités applicatifs vers les schémas de réponse."""
from app.application.dto import dto
from app.presentation.schemas import auth as sa
from app.presentation.schemas import messaging as sm
from app.presentation.schemas import properties as sp
from app.presentation.schemas import social as ss


def user_out(v: dto.UserView) -> sa.UserOut:
    return sa.UserOut(id=v.user.id, email=v.user.email, status=v.user.status, roles=v.roles,
                      profile=sa.ProfileOut.model_validate(v.profile) if v.profile else None, created_at=v.user.created_at)


def public_user_out(v: dto.UserView) -> sa.PublicUserOut:
    p = v.profile
    return sa.PublicUserOut(id=v.user.id, first_name=p.first_name if p else "", last_name=(p.last_name[:1] + ".") if p and p.last_name else "",
                            bio=p.bio if p else None, city_id=p.city_id if p else None,
                            roles=[r for r in v.roles if r != "ADMIN"], rating_avg=v.rating_avg, rating_count=v.rating_count)


def card_out(c: dto.PropertyCard) -> sp.PropertyCardOut:
    p = c.property
    return sp.PropertyCardOut(id=p.id, title=p.title, price=p.price, rooms=p.rooms, surface_m2=p.surface_m2, city_id=p.city_id,
                              city_name=c.city_name, coliving_allowed=p.coliving_allowed, max_roommates=p.max_roommates,
                              status=p.status, latitude=p.latitude, longitude=p.longitude, cover=c.cover,
                              is_favorite=c.is_favorite, created_at=p.created_at)


def detail_out(d: dto.PropertyDetail) -> sp.PropertyDetailOut:
    base = sp.PropertyOut.model_validate(d.property).model_dump()
    return sp.PropertyDetailOut(**base, city_name=d.city_name, category_name=d.category_name,
                                images=[sp.ImageOut.model_validate(i) for i in d.images], owner_name=d.owner_name,
                                owner_rating_avg=d.owner_rating_avg, is_favorite=d.is_favorite)


def group_out(v: dto.GroupView) -> ss.GroupOut:
    return ss.GroupOut(id=v.group.id, name=v.group.name, creator_id=v.group.creator_id, max_members=v.group.max_members,
                       members=[ss.MemberOut(user_id=m.user_id, name=n, role=m.role) for m, n in v.members],
                       conversation_id=v.conversation_id)


def rental_out(v: dto.RentalRequestView) -> ss.RentalRequestOut:
    r = v.request
    return ss.RentalRequestOut(id=r.id, property_id=r.property_id, property_title=v.property_title, applicant_label=v.applicant_label,
                               applicant_user_id=r.applicant_user_id, group_id=r.group_id, message=r.message,
                               desired_move_in=r.desired_move_in, status=r.status, created_at=r.created_at)


def visit_out(v: dto.VisitView) -> ss.VisitOut:
    return ss.VisitOut(id=v.visit.id, property_id=v.visit.property_id, property_title=v.property_title,
                       requester_id=v.visit.requester_id, status=v.visit.status.value, note=v.visit.note,
                       slots=[ss.SlotOut.model_validate(s) for s in v.slots])


def message_out(v: dto.MessageView) -> sm.MessageOut:
    m = v.message
    return sm.MessageOut(id=m.id, conversation_id=m.conversation_id, sender_id=m.sender_id, body=m.body,
                         property_id=m.property_id, created_at=m.created_at, status=v.status,
                         attachments=[sm.AttachmentOut.model_validate(a) for a in v.attachments])


def conversation_out(v: dto.ConversationView) -> sm.ConversationOut:
    last = message_out(dto.MessageView(v.last_message, [], "sent")) if v.last_message else None
    return sm.ConversationOut(id=v.conversation.id, type=v.conversation.type, title=v.title, member_ids=v.member_ids,
                              last_message=last, unread_count=v.unread_count)
