SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_reason_records`;
CREATE TABLE `chat_reason_records` (
                                       `id` bigint NOT NULL AUTO_INCREMENT,
                                       `uid` varchar(128) NOT NULL COMMENT 'User ID',
                                       `chat_id` bigint NOT NULL COMMENT 'Chat session ID',
                                       `req_id` bigint NOT NULL COMMENT 'Request ID',
                                       `content` longtext NOT NULL COMMENT 'Reasoning thought content',
                                       `thinking_elapsed_secs` bigint DEFAULT '0' COMMENT 'Thinking elapsed time (seconds)',
                                       `type` varchar(50) DEFAULT NULL COMMENT 'Reasoning type (e.g.: x1_math)',
                                       `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
                                       `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
                                       PRIMARY KEY (`id`,`create_time`),
                                       KEY `idx_uid` (`uid`),
                                       KEY `idx_chat_id` (`chat_id`),
                                       KEY `idx_req_id` (`req_id`),
                                       KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chat thinking record table';

SET FOREIGN_KEY_CHECKS = 1;