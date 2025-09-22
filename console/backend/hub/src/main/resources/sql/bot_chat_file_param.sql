CREATE TABLE `bot_chat_file_param`
(
    `id`          BIGINT AUTO_INCREMENT PRIMARY KEY COMMENT 'Primary key ID',
    `uid`         BIGINT       NOT NULL COMMENT 'User ID',
    `chat_id`     BIGINT       NOT NULL COMMENT 'Chat ID',
    `name`        VARCHAR(255) NOT NULL COMMENT 'Parameter name',
    `file_ids`    JSON COMMENT 'File ID list',
    `file_urls`   JSON COMMENT 'File URL list',
    `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
    `update_time` DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
    `is_delete`   TINYINT  DEFAULT 0 COMMENT 'Whether deleted 0-not deleted 1-deleted',

    -- Index
    INDEX         `idx_uid` (`uid`),
    INDEX         `idx_chat_id` (`chat_id`),
    INDEX         `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='Assistant Q&A file parameter information table';