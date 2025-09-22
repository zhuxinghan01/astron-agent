-- H2 database test table structure
DROP TABLE IF EXISTS user_info;

CREATE TABLE user_info (
    id BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Non-business primary key',
    uid BIGINT COMMENT 'UID',
    username VARCHAR(255) COMMENT 'Username',
    avatar VARCHAR(512) COMMENT 'Avatar',
    nickname VARCHAR(255) COMMENT 'User nickname',
    mobile VARCHAR(255) NOT NULL COMMENT 'Mobile number',
    account_status TINYINT DEFAULT 0 COMMENT 'Activation status: 0 not activated, 1 activated, 2 frozen',
    user_agreement TINYINT DEFAULT 0 COMMENT 'Whether agreed to user agreement: 0 not agreed, 1 agreed',
    deleted TINYINT DEFAULT 0 COMMENT 'Logical deletion flag: 0 not deleted, 1 deleted',
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Create time',
    update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time'
);

-- Create indexes
CREATE UNIQUE INDEX ux_user_info_uid ON user_info (uid);
CREATE INDEX idx_user_info_create_time ON user_info (create_time);
CREATE INDEX idx_user_info_mobile ON user_info (mobile);
CREATE INDEX idx_user_info_username ON user_info (username);
CREATE INDEX idx_user_info_nickname ON user_info (nickname);
CREATE INDEX idx_user_info_deleted ON user_info (deleted);