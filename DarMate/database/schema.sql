CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 0001

CREATE TABLE application_setting (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    setting_key VARCHAR(100) NOT NULL, 
    value TEXT NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (setting_key)
);

CREATE TABLE property_category (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    name VARCHAR(80) NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE region (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    name VARCHAR(100) NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE `role` (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    name VARCHAR(30) NOT NULL, 
    PRIMARY KEY (id), 
    UNIQUE (name)
);

CREATE TABLE user (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    email VARCHAR(255) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    status VARCHAR(20) NOT NULL, 
    failed_login_count INTEGER NOT NULL, 
    locked_until DATETIME, 
    last_login_at DATETIME, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    updated_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id)
);

CREATE UNIQUE INDEX ix_user_email ON user (email);

CREATE INDEX ix_user_status ON user (status);

CREATE TABLE audit_log (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT, 
    action VARCHAR(80) NOT NULL, 
    entity_type VARCHAR(50), 
    entity_id BIGINT, 
    details JSON, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE SET NULL
);

CREATE INDEX ix_audit_log_action ON audit_log (action);

CREATE INDEX ix_audit_log_user_id ON audit_log (user_id);

CREATE TABLE city (
    id INTEGER NOT NULL AUTO_INCREMENT, 
    region_id INTEGER NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(region_id) REFERENCES region (id) ON DELETE RESTRICT, 
    UNIQUE (region_id, name)
);

CREATE INDEX ix_city_region_id ON city (region_id);

CREATE TABLE identity_document (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT NOT NULL, 
    path VARCHAR(255) NOT NULL, 
    doc_type VARCHAR(30) NOT NULL, 
    status VARCHAR(20) NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE
);

CREATE INDEX ix_identity_document_user_id ON identity_document (user_id);

CREATE TABLE notification (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT NOT NULL, 
    type VARCHAR(30) NOT NULL, 
    title VARCHAR(150) NOT NULL, 
    body TEXT, 
    link VARCHAR(255), 
    is_read BOOL NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE
);

CREATE INDEX ix_notification_user_read ON notification (user_id, is_read);

CREATE TABLE password_reset_token (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT NOT NULL, 
    token_hash VARCHAR(64) NOT NULL, 
    expires_at DATETIME NOT NULL, 
    used_at DATETIME, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (token_hash)
);

CREATE INDEX ix_password_reset_token_user_id ON password_reset_token (user_id);

CREATE TABLE refresh_token (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT NOT NULL, 
    token_hash VARCHAR(64) NOT NULL, 
    expires_at DATETIME NOT NULL, 
    revoked_at DATETIME, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (token_hash)
);

CREATE INDEX ix_refresh_token_user_id ON refresh_token (user_id);

CREATE TABLE report (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    reporter_id BIGINT NOT NULL, 
    reported_user_id BIGINT, 
    message_id BIGINT, 
    reason VARCHAR(100) NOT NULL, 
    details TEXT, 
    status VARCHAR(20) NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(reported_user_id) REFERENCES user (id) ON DELETE SET NULL, 
    FOREIGN KEY(reporter_id) REFERENCES user (id) ON DELETE CASCADE
);

CREATE TABLE roommate_group (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    name VARCHAR(100) NOT NULL, 
    creator_id BIGINT NOT NULL, 
    max_members INTEGER NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(creator_id) REFERENCES user (id) ON DELETE RESTRICT
);

CREATE TABLE roommate_request (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    sender_id BIGINT NOT NULL, 
    receiver_id BIGINT NOT NULL, 
    message TEXT, 
    status VARCHAR(20) NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(receiver_id) REFERENCES user (id) ON DELETE CASCADE, 
    FOREIGN KEY(sender_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (sender_id, receiver_id)
);

CREATE INDEX ix_roommate_request_receiver_id ON roommate_request (receiver_id);

CREATE TABLE saved_search (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    filters JSON NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE
);

CREATE INDEX ix_saved_search_user_id ON saved_search (user_id);

CREATE TABLE user_block (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    blocker_id BIGINT NOT NULL, 
    blocked_id BIGINT NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(blocked_id) REFERENCES user (id) ON DELETE CASCADE, 
    FOREIGN KEY(blocker_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (blocker_id, blocked_id)
);

CREATE TABLE user_role (
    user_id BIGINT NOT NULL, 
    role_id INTEGER NOT NULL, 
    PRIMARY KEY (user_id, role_id), 
    FOREIGN KEY(role_id) REFERENCES `role` (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE
);

CREATE TABLE conversation (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    type VARCHAR(10) NOT NULL, 
    group_id BIGINT, 
    private_key VARCHAR(50), 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(group_id) REFERENCES roommate_group (id) ON DELETE CASCADE, 
    UNIQUE (group_id), 
    UNIQUE (private_key)
);

CREATE TABLE group_invitation (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    group_id BIGINT NOT NULL, 
    inviter_id BIGINT NOT NULL, 
    invitee_id BIGINT NOT NULL, 
    status VARCHAR(20) NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(group_id) REFERENCES roommate_group (id) ON DELETE CASCADE, 
    FOREIGN KEY(invitee_id) REFERENCES user (id) ON DELETE CASCADE, 
    FOREIGN KEY(inviter_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (group_id, invitee_id, status)
);

CREATE INDEX ix_group_invitation_invitee_id ON group_invitation (invitee_id);

CREATE TABLE group_member (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    group_id BIGINT NOT NULL, 
    user_id BIGINT NOT NULL, 
    `role` VARCHAR(10) NOT NULL, 
    joined_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(group_id) REFERENCES roommate_group (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (group_id, user_id)
);

CREATE INDEX ix_group_member_user_id ON group_member (user_id);

CREATE TABLE property (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    owner_id BIGINT NOT NULL, 
    city_id INTEGER NOT NULL, 
    category_id INTEGER NOT NULL, 
    title VARCHAR(150) NOT NULL, 
    description TEXT NOT NULL, 
    price NUMERIC(10, 2) NOT NULL, 
    rooms INTEGER NOT NULL, 
    surface_m2 INTEGER, 
    address VARCHAR(255), 
    latitude NUMERIC(9, 6), 
    longitude NUMERIC(9, 6), 
    coliving_allowed BOOL NOT NULL, 
    max_roommates INTEGER NOT NULL, 
    conditions TEXT, 
    available_from DATE, 
    status VARCHAR(20) NOT NULL, 
    view_count INTEGER NOT NULL, 
    deleted_at DATETIME, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    updated_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(category_id) REFERENCES property_category (id) ON DELETE RESTRICT, 
    FOREIGN KEY(city_id) REFERENCES city (id) ON DELETE RESTRICT, 
    FOREIGN KEY(owner_id) REFERENCES user (id) ON DELETE RESTRICT
);

CREATE INDEX ix_property_owner_id ON property (owner_id);

CREATE INDEX ix_property_search ON property (city_id, price, status);

CREATE TABLE roommate_profile (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT NOT NULL, 
    city_id INTEGER, 
    budget_min NUMERIC(10, 2), 
    budget_max NUMERIC(10, 2), 
    smoker BOOL NOT NULL, 
    has_pets BOOL NOT NULL, 
    schedule VARCHAR(20) NOT NULL, 
    cleanliness INTEGER NOT NULL, 
    sociability INTEGER NOT NULL, 
    about TEXT, 
    is_active BOOL NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(city_id) REFERENCES city (id) ON DELETE SET NULL, 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (user_id)
);

CREATE INDEX ix_roommate_profile_city_id ON roommate_profile (city_id);

CREATE TABLE search_alert (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    saved_search_id BIGINT NOT NULL, 
    is_active BOOL NOT NULL, 
    last_notified_at DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(saved_search_id) REFERENCES saved_search (id) ON DELETE CASCADE, 
    UNIQUE (saved_search_id)
);

CREATE TABLE user_profile (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT NOT NULL, 
    first_name VARCHAR(80) NOT NULL, 
    last_name VARCHAR(80) NOT NULL, 
    phone VARCHAR(30), 
    bio TEXT, 
    birth_date DATE, 
    city_id INTEGER, 
    language VARCHAR(5) NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(city_id) REFERENCES city (id) ON DELETE SET NULL, 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (user_id)
);

CREATE TABLE conversation_member (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    conversation_id BIGINT NOT NULL, 
    user_id BIGINT NOT NULL, 
    last_read_at DATETIME, 
    PRIMARY KEY (id), 
    FOREIGN KEY(conversation_id) REFERENCES conversation (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (conversation_id, user_id)
);

CREATE INDEX ix_conversation_member_user_id ON conversation_member (user_id);

CREATE TABLE favorite (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    user_id BIGINT NOT NULL, 
    property_id BIGINT NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(property_id) REFERENCES property (id) ON DELETE CASCADE, 
    FOREIGN KEY(user_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (user_id, property_id)
);

CREATE INDEX ix_favorite_user_id ON favorite (user_id);

CREATE TABLE message (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    conversation_id BIGINT NOT NULL, 
    sender_id BIGINT NOT NULL, 
    body TEXT, 
    property_id BIGINT, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(conversation_id) REFERENCES conversation (id) ON DELETE CASCADE, 
    FOREIGN KEY(property_id) REFERENCES property (id) ON DELETE SET NULL, 
    FOREIGN KEY(sender_id) REFERENCES user (id) ON DELETE RESTRICT
);

CREATE INDEX ix_message_conv_created ON message (conversation_id, created_at);

CREATE TABLE property_image (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    property_id BIGINT NOT NULL, 
    path VARCHAR(255) NOT NULL, 
    position INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(property_id) REFERENCES property (id) ON DELETE CASCADE
);

CREATE INDEX ix_property_image_property_id ON property_image (property_id);

CREATE TABLE rental_request (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    property_id BIGINT NOT NULL, 
    created_by_id BIGINT NOT NULL, 
    applicant_user_id BIGINT, 
    group_id BIGINT, 
    message TEXT, 
    desired_move_in DATE, 
    status VARCHAR(20) NOT NULL, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    updated_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    CONSTRAINT ck_rental_single_applicant CHECK ((applicant_user_id IS NOT NULL) <> (group_id IS NOT NULL)), 
    FOREIGN KEY(applicant_user_id) REFERENCES user (id) ON DELETE RESTRICT, 
    FOREIGN KEY(created_by_id) REFERENCES user (id) ON DELETE RESTRICT, 
    FOREIGN KEY(group_id) REFERENCES roommate_group (id) ON DELETE RESTRICT, 
    FOREIGN KEY(property_id) REFERENCES property (id) ON DELETE RESTRICT
);

CREATE INDEX ix_rental_request_applicant_user_id ON rental_request (applicant_user_id);

CREATE INDEX ix_rental_request_group_id ON rental_request (group_id);

CREATE INDEX ix_rental_request_property_id ON rental_request (property_id);

CREATE TABLE message_attachment (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    message_id BIGINT NOT NULL, 
    path VARCHAR(255) NOT NULL, 
    original_name VARCHAR(255) NOT NULL, 
    mime_type VARCHAR(100) NOT NULL, 
    size_bytes INTEGER NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(message_id) REFERENCES message (id) ON DELETE CASCADE
);

CREATE INDEX ix_message_attachment_message_id ON message_attachment (message_id);

CREATE TABLE review (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    rental_request_id BIGINT NOT NULL, 
    reviewer_id BIGINT NOT NULL, 
    reviewee_id BIGINT NOT NULL, 
    property_id BIGINT NOT NULL, 
    target_type VARCHAR(20) NOT NULL, 
    rating INTEGER NOT NULL, 
    comment TEXT, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    CONSTRAINT ck_review_rating CHECK (rating BETWEEN 1 AND 5), 
    FOREIGN KEY(property_id) REFERENCES property (id) ON DELETE CASCADE, 
    FOREIGN KEY(rental_request_id) REFERENCES rental_request (id) ON DELETE CASCADE, 
    FOREIGN KEY(reviewee_id) REFERENCES user (id) ON DELETE CASCADE, 
    FOREIGN KEY(reviewer_id) REFERENCES user (id) ON DELETE CASCADE, 
    UNIQUE (rental_request_id, reviewer_id, target_type, reviewee_id)
);

CREATE INDEX ix_review_property_id ON review (property_id);

CREATE INDEX ix_review_reviewee_id ON review (reviewee_id);

CREATE TABLE visit (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    property_id BIGINT NOT NULL, 
    requester_id BIGINT NOT NULL, 
    rental_request_id BIGINT, 
    status VARCHAR(20) NOT NULL, 
    note TEXT, 
    created_at DATETIME NOT NULL DEFAULT (CURRENT_TIMESTAMP), 
    PRIMARY KEY (id), 
    FOREIGN KEY(property_id) REFERENCES property (id) ON DELETE CASCADE, 
    FOREIGN KEY(rental_request_id) REFERENCES rental_request (id) ON DELETE SET NULL, 
    FOREIGN KEY(requester_id) REFERENCES user (id) ON DELETE CASCADE
);

CREATE INDEX ix_visit_property_id ON visit (property_id);

CREATE INDEX ix_visit_requester_id ON visit (requester_id);

CREATE TABLE visit_slot (
    id BIGINT NOT NULL AUTO_INCREMENT, 
    visit_id BIGINT NOT NULL, 
    proposed_by_id BIGINT NOT NULL, 
    starts_at DATETIME NOT NULL, 
    ends_at DATETIME NOT NULL, 
    is_selected BOOL NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(proposed_by_id) REFERENCES user (id) ON DELETE CASCADE, 
    FOREIGN KEY(visit_id) REFERENCES visit (id) ON DELETE CASCADE
);

CREATE INDEX ix_visit_slot_visit_id ON visit_slot (visit_id);

INSERT INTO alembic_version (version_num) VALUES ('0001');

