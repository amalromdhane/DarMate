# Dictionnaire de données DarMate

Généré automatiquement depuis les modèles SQLAlchemy (33 tables).


## `application_setting`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| setting_key | VARCHAR(100) | non | UNIQUE |
| value | TEXT | non |  |

## `audit_log`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | oui | FK → user.id (ON DELETE SET NULL), INDEX |
| action | VARCHAR(80) | non | INDEX |
| entity_type | VARCHAR(50) | oui |  |
| entity_id | BIGINT | oui |  |
| details | JSON | oui |  |
| created_at | DATETIME | non |  |

## `city`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | INTEGER | non | PK |
| region_id | INTEGER | non | FK → region.id (ON DELETE RESTRICT), INDEX |
| name | VARCHAR(100) | non |  |

Contraintes/index composés : UniqueConstraint: region_id,name

## `conversation`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| type | VARCHAR(10) | non |  |
| group_id | BIGINT | oui | FK → roommate_group.id (ON DELETE CASCADE), UNIQUE |
| private_key | VARCHAR(50) | oui | UNIQUE |
| created_at | DATETIME | non |  |

## `conversation_member`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| conversation_id | BIGINT | non | FK → conversation.id (ON DELETE CASCADE) |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| last_read_at | DATETIME | oui |  |

Contraintes/index composés : UniqueConstraint: conversation_id,user_id

## `favorite`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| property_id | BIGINT | non | FK → property.id (ON DELETE CASCADE) |
| created_at | DATETIME | non |  |

Contraintes/index composés : UniqueConstraint: user_id,property_id

## `group_invitation`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| group_id | BIGINT | non | FK → roommate_group.id (ON DELETE CASCADE) |
| inviter_id | BIGINT | non | FK → user.id (ON DELETE CASCADE) |
| invitee_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| status | VARCHAR(20) | non |  |
| created_at | DATETIME | non |  |

Contraintes/index composés : UniqueConstraint: group_id,invitee_id,status

## `group_member`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| group_id | BIGINT | non | FK → roommate_group.id (ON DELETE CASCADE) |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| role | VARCHAR(10) | non |  |
| joined_at | DATETIME | non |  |

Contraintes/index composés : UniqueConstraint: group_id,user_id

## `identity_document`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| path | VARCHAR(255) | non |  |
| doc_type | VARCHAR(30) | non |  |
| status | VARCHAR(20) | non |  |
| created_at | DATETIME | non |  |

## `message`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| conversation_id | BIGINT | non | FK → conversation.id (ON DELETE CASCADE) |
| sender_id | BIGINT | non | FK → user.id (ON DELETE RESTRICT) |
| body | TEXT | oui |  |
| property_id | BIGINT | oui | FK → property.id (ON DELETE SET NULL) |
| created_at | DATETIME | non |  |

Contraintes/index composés : ix_message_conv_created(conversation_id, created_at)

## `message_attachment`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| message_id | BIGINT | non | FK → message.id (ON DELETE CASCADE), INDEX |
| path | VARCHAR(255) | non |  |
| original_name | VARCHAR(255) | non |  |
| mime_type | VARCHAR(100) | non |  |
| size_bytes | INTEGER | non |  |

## `notification`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE) |
| type | VARCHAR(30) | non |  |
| title | VARCHAR(150) | non |  |
| body | TEXT | oui |  |
| link | VARCHAR(255) | oui |  |
| is_read | BOOLEAN | non |  |
| created_at | DATETIME | non |  |

Contraintes/index composés : ix_notification_user_read(user_id, is_read)

## `password_reset_token`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| token_hash | VARCHAR(64) | non | UNIQUE |
| expires_at | DATETIME | non |  |
| used_at | DATETIME | oui |  |
| created_at | DATETIME | non |  |

## `property`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| owner_id | BIGINT | non | FK → user.id (ON DELETE RESTRICT), INDEX |
| city_id | INTEGER | non | FK → city.id (ON DELETE RESTRICT) |
| category_id | INTEGER | non | FK → property_category.id (ON DELETE RESTRICT) |
| title | VARCHAR(150) | non |  |
| description | TEXT | non |  |
| price | NUMERIC(10, 2) | non |  |
| rooms | INTEGER | non |  |
| surface_m2 | INTEGER | oui |  |
| address | VARCHAR(255) | oui |  |
| latitude | NUMERIC(9, 6) | oui |  |
| longitude | NUMERIC(9, 6) | oui |  |
| coliving_allowed | BOOLEAN | non |  |
| max_roommates | INTEGER | non |  |
| conditions | TEXT | oui |  |
| available_from | DATE | oui |  |
| status | VARCHAR(20) | non |  |
| view_count | INTEGER | non |  |
| deleted_at | DATETIME | oui |  |
| created_at | DATETIME | non |  |
| updated_at | DATETIME | non |  |

Contraintes/index composés : ix_property_search(city_id, price, status)

## `property_category`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | INTEGER | non | PK |
| name | VARCHAR(80) | non | UNIQUE |

## `property_image`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| property_id | BIGINT | non | FK → property.id (ON DELETE CASCADE), INDEX |
| path | VARCHAR(255) | non |  |
| position | INTEGER | non |  |

## `refresh_token`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| token_hash | VARCHAR(64) | non | UNIQUE |
| expires_at | DATETIME | non |  |
| revoked_at | DATETIME | oui |  |
| created_at | DATETIME | non |  |

## `region`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | INTEGER | non | PK |
| name | VARCHAR(100) | non | UNIQUE |

## `rental_request`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| property_id | BIGINT | non | FK → property.id (ON DELETE RESTRICT), INDEX |
| created_by_id | BIGINT | non | FK → user.id (ON DELETE RESTRICT) |
| applicant_user_id | BIGINT | oui | FK → user.id (ON DELETE RESTRICT), INDEX |
| group_id | BIGINT | oui | FK → roommate_group.id (ON DELETE RESTRICT), INDEX |
| message | TEXT | oui |  |
| desired_move_in | DATE | oui |  |
| status | VARCHAR(20) | non |  |
| created_at | DATETIME | non |  |
| updated_at | DATETIME | non |  |

Contraintes/index composés : CheckConstraint: ck_rental_single_applicant

## `report`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| reporter_id | BIGINT | non | FK → user.id (ON DELETE CASCADE) |
| reported_user_id | BIGINT | oui | FK → user.id (ON DELETE SET NULL) |
| message_id | BIGINT | oui |  |
| reason | VARCHAR(100) | non |  |
| details | TEXT | oui |  |
| status | VARCHAR(20) | non |  |
| created_at | DATETIME | non |  |

## `review`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| rental_request_id | BIGINT | non | FK → rental_request.id (ON DELETE CASCADE) |
| reviewer_id | BIGINT | non | FK → user.id (ON DELETE CASCADE) |
| reviewee_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| property_id | BIGINT | non | FK → property.id (ON DELETE CASCADE), INDEX |
| target_type | VARCHAR(20) | non |  |
| rating | INTEGER | non |  |
| comment | TEXT | oui |  |
| created_at | DATETIME | non |  |

Contraintes/index composés : UniqueConstraint: rental_request_id,reviewer_id,target_type,reviewee_id; CheckConstraint: ck_review_rating

## `role`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | INTEGER | non | PK |
| name | VARCHAR(30) | non | UNIQUE |

## `roommate_group`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| name | VARCHAR(100) | non |  |
| creator_id | BIGINT | non | FK → user.id (ON DELETE RESTRICT) |
| max_members | INTEGER | non |  |
| created_at | DATETIME | non |  |

## `roommate_profile`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), UNIQUE |
| city_id | INTEGER | oui | FK → city.id (ON DELETE SET NULL), INDEX |
| budget_min | NUMERIC(10, 2) | oui |  |
| budget_max | NUMERIC(10, 2) | oui |  |
| smoker | BOOLEAN | non |  |
| has_pets | BOOLEAN | non |  |
| schedule | VARCHAR(20) | non |  |
| cleanliness | INTEGER | non |  |
| sociability | INTEGER | non |  |
| about | TEXT | oui |  |
| is_active | BOOLEAN | non |  |

## `roommate_request`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| sender_id | BIGINT | non | FK → user.id (ON DELETE CASCADE) |
| receiver_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| message | TEXT | oui |  |
| status | VARCHAR(20) | non |  |
| created_at | DATETIME | non |  |

Contraintes/index composés : UniqueConstraint: sender_id,receiver_id

## `saved_search`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| name | VARCHAR(100) | non |  |
| filters | JSON | non |  |
| created_at | DATETIME | non |  |

## `search_alert`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| saved_search_id | BIGINT | non | FK → saved_search.id (ON DELETE CASCADE), UNIQUE |
| is_active | BOOLEAN | non |  |
| last_notified_at | DATETIME | oui |  |

## `user`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| email | VARCHAR(255) | non | UNIQUE, INDEX |
| password_hash | VARCHAR(255) | non |  |
| status | VARCHAR(20) | non | INDEX |
| failed_login_count | INTEGER | non |  |
| locked_until | DATETIME | oui |  |
| last_login_at | DATETIME | oui |  |
| created_at | DATETIME | non |  |
| updated_at | DATETIME | non |  |

## `user_block`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| blocker_id | BIGINT | non | FK → user.id (ON DELETE CASCADE) |
| blocked_id | BIGINT | non | FK → user.id (ON DELETE CASCADE) |

Contraintes/index composés : UniqueConstraint: blocker_id,blocked_id

## `user_profile`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| user_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), UNIQUE |
| first_name | VARCHAR(80) | non |  |
| last_name | VARCHAR(80) | non |  |
| phone | VARCHAR(30) | oui |  |
| bio | TEXT | oui |  |
| birth_date | DATE | oui |  |
| city_id | INTEGER | oui | FK → city.id (ON DELETE SET NULL) |
| language | VARCHAR(5) | non |  |

## `user_role`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| user_id | BIGINT | non | PK, FK → user.id (ON DELETE CASCADE) |
| role_id | INTEGER | non | PK, FK → role.id (ON DELETE CASCADE) |

## `visit`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| property_id | BIGINT | non | FK → property.id (ON DELETE CASCADE), INDEX |
| requester_id | BIGINT | non | FK → user.id (ON DELETE CASCADE), INDEX |
| rental_request_id | BIGINT | oui | FK → rental_request.id (ON DELETE SET NULL) |
| status | VARCHAR(20) | non |  |
| note | TEXT | oui |  |
| created_at | DATETIME | non |  |

## `visit_slot`

| Colonne | Type | Null | Clé / contrainte |
|---|---|---|---|
| id | BIGINT | non | PK |
| visit_id | BIGINT | non | FK → visit.id (ON DELETE CASCADE), INDEX |
| proposed_by_id | BIGINT | non | FK → user.id (ON DELETE CASCADE) |
| starts_at | DATETIME | non |  |
| ends_at | DATETIME | non |  |
| is_selected | BOOLEAN | non |  |
