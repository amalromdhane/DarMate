# Diagramme ERD (33 tables)

```mermaid
erDiagram
    USER ||--|| USER_PROFILE : has
    USER ||--o{ USER_ROLE : has
    ROLE ||--o{ USER_ROLE : grants
    USER ||--o{ REFRESH_TOKEN : owns
    USER ||--o{ PASSWORD_RESET_TOKEN : requests
    USER ||--o{ IDENTITY_DOCUMENT : uploads
    USER ||--o{ USER_BLOCK : blocks
    USER ||--o{ AUDIT_LOG : triggers
    USER ||--o{ REPORT : files
    REGION ||--o{ CITY : contains
    CITY ||--o{ PROPERTY : located_in
    PROPERTY_CATEGORY ||--o{ PROPERTY : classifies
    USER ||--o{ PROPERTY : owns
    PROPERTY ||--o{ PROPERTY_IMAGE : has
    USER ||--o{ FAVORITE : saves
    PROPERTY ||--o{ FAVORITE : favorited
    USER ||--o{ SAVED_SEARCH : creates
    SAVED_SEARCH ||--o| SEARCH_ALERT : triggers
    USER ||--o| ROOMMATE_PROFILE : has
    USER ||--o{ ROOMMATE_REQUEST : sends_receives
    USER ||--o{ ROOMMATE_GROUP : creates
    ROOMMATE_GROUP ||--o{ GROUP_MEMBER : has
    USER ||--o{ GROUP_MEMBER : joins
    ROOMMATE_GROUP ||--o{ GROUP_INVITATION : issues
    PROPERTY ||--o{ RENTAL_REQUEST : receives
    USER ||--o{ RENTAL_REQUEST : applies
    ROOMMATE_GROUP ||--o{ RENTAL_REQUEST : applies_as_group
    PROPERTY ||--o{ VISIT : visited
    VISIT ||--o{ VISIT_SLOT : proposes
    RENTAL_REQUEST ||--o{ REVIEW : enables
    USER ||--o{ REVIEW : writes
    ROOMMATE_GROUP ||--o| CONVERSATION : discusses
    CONVERSATION ||--o{ CONVERSATION_MEMBER : has
    CONVERSATION ||--o{ MESSAGE : contains
    MESSAGE ||--o{ MESSAGE_ATTACHMENT : has
    USER ||--o{ NOTIFICATION : receives
```

Règles clés : `rental_request` a exactement un demandeur (utilisateur **ou** groupe, contrainte CHECK) ;
`review` n'est créée que pour une demande `CONFIRMED` (vérifié par le use case) ; suppression logique des annonces (`deleted_at`).
Détail des colonnes : `data-dictionary.md`.
