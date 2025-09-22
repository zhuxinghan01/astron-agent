SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `share_chat`;
CREATE TABLE `share_chat` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Corresponds to share_key in chat_share_content',
  `uid` varchar(128) DEFAULT NULL COMMENT 'UID of sharing user',
  `url_key` varchar(64) DEFAULT NULL COMMENT 'Key parameter for frontend URL, anti-scraping',
  `chat_id` bigint DEFAULT NULL COMMENT 'Primary key of shared conversation in chat_list',
  `bot_id` bigint DEFAULT '0' COMMENT 'Assistant ID in assistant mode, 0 for normal mode',
  `click_times` int DEFAULT '0' COMMENT 'Click count',
  `max_click_times` int DEFAULT '-1' COMMENT 'Redundant, can limit max click times, default -1 means unlimited',
  `url_status` tinyint DEFAULT '1' COMMENT 'Whether URL is valid: 0 Invalid, 1 Valid',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `enabled_plugin_ids` varchar(255) DEFAULT '' COMMENT 'Enabled plugin IDs for current conversation list',
  `like_times` int NOT NULL DEFAULT '0' COMMENT 'Like count',
  `ip_location` varchar(32) DEFAULT '' COMMENT 'IP location when sharing',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_url_key` (`url_key`) USING BTREE,
  KEY `idx_bot_id` (`bot_id`),
  KEY `idx_enabled_plugin_ids` (`enabled_plugin_ids`),
  KEY `idx_create_time` (`create_time`),
  KEY `idx_uid` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Conversation sharing information index table';

SET FOREIGN_KEY_CHECKS = 1;