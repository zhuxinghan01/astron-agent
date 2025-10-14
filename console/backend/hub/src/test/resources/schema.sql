-- H2 database test table structure
DROP TABLE IF EXISTS user_info;

CREATE TABLE `user_info` (
    `id`             bigint NOT NULL AUTO_INCREMENT COMMENT 'Non-business primary key',
    `uid`            varchar(128)                                                  DEFAULT NULL COMMENT 'UID',
    `username`       varchar(255)                                                  DEFAULT NULL COMMENT 'Username',
    `avatar`         varchar(512)                                                  DEFAULT NULL COMMENT 'Avatar',
    `nickname`       varchar(255)                                                  DEFAULT NULL COMMENT 'User nickname',
    `mobile`         varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL COMMENT 'Mobile number',
    `account_status` tinyint                                                       DEFAULT '0' COMMENT 'Activation status: 0 inactive, 1 active, 2 frozen',
    `enterprise_service_type` int                                                  DEFAULT '0' COMMENT 'Enterprise service type: 0 none, 1 team, 2 enterprise',
    `user_agreement` tinyint                                                       DEFAULT '0' COMMENT 'Whether agreed to user agreement: 0 not agreed, 1 agreed',
    `deleted`        tinyint                                                       DEFAULT '0' COMMENT 'Logical deletion flag: 0 not deleted, 1 deleted',
    `create_time`    datetime                                                      DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
    `update_time`    datetime                                                      DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uid_unique_index` (`uid`),
    KEY              `idx_create_time` (`create_time`),
    KEY              `index_mobile` (`mobile`),
    KEY              `idx_username` (`username`),
    KEY              `idx_nickname` (`nickname`),
    KEY              `idx_deleted` (`deleted`)
);

-- Create indexes
CREATE UNIQUE INDEX ux_user_info_uid ON user_info (uid);
CREATE INDEX idx_user_info_create_time ON user_info (create_time);
CREATE INDEX idx_user_info_mobile ON user_info (mobile);
CREATE INDEX idx_user_info_username ON user_info (username);
CREATE INDEX idx_user_info_nickname ON user_info (nickname);
CREATE INDEX idx_user_info_deleted ON user_info (deleted);