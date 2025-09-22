SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_bot_remove`;
CREATE TABLE `chat_bot_remove` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bot_id` int DEFAULT NULL COMMENT 'botId',
  `uid` varchar(128) DEFAULT NULL COMMENT 'Publisher UID',
  `bot_name` varchar(48) DEFAULT NULL COMMENT 'Bot name, this is a copy of the original from the creator',
  `bot_type` tinyint DEFAULT '1' COMMENT 'Bot type: 1 Custom Assistant, 2 Life Assistant, 3 Work Assistant, 4 Marketing Assistant, 5 Writing Expert, 6 Knowledge Expert',
  `avatar` varchar(512) DEFAULT NULL COMMENT 'Bot avatar URL',
  `prompt` varchar(2048) DEFAULT NULL COMMENT 'Bot prompt',
  `bot_desc` varchar(255) DEFAULT NULL COMMENT 'Bot description',
  `block_reason` varchar(255) DEFAULT NULL COMMENT 'Reason for review rejection',
  `is_delete` tinyint DEFAULT '0' COMMENT 'Application history: 0 Not deleted, 1 Deleted',
  `audit_time` datetime DEFAULT NULL COMMENT 'Audit time',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_bot_id` (`bot_id`),
  KEY `idx_bot_type` (`bot_type`),
  KEY `idx_create_time4` (`create_time`),
  KEY `uid_index` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Bot deletion record table';

SET FOREIGN_KEY_CHECKS = 1;