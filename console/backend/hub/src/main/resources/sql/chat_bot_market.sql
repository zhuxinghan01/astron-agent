SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_bot_market`;
CREATE TABLE `chat_bot_market` (
  `id` int NOT NULL AUTO_INCREMENT,
  `bot_id` int DEFAULT NULL COMMENT 'botId',
  `uid` varchar(128) DEFAULT NULL COMMENT 'Publisher UID',
  `bot_name` varchar(48) DEFAULT NULL COMMENT 'Bot name, this is a copy of the original from the creator',
  `bot_type` tinyint DEFAULT '1' COMMENT 'Bot type: 1 Custom Assistant, 2 Life Assistant, 3 Work Assistant, 4 Marketing Assistant, 5 Writing Expert, 6 Knowledge Expert',
  `avatar` varchar(1024) DEFAULT NULL COMMENT 'Bot avatar',
  `pc_background` varchar(512) DEFAULT '' COMMENT 'PC chat background image',
  `app_background` varchar(512) DEFAULT '' COMMENT 'Mobile chat background image',
  `background_color` tinyint DEFAULT '0' COMMENT 'Background image brightness: 0 Light, 1 Dark',
  `prompt` varchar(2048) DEFAULT NULL COMMENT 'Bot prompt',
  `prologue` varchar(512) DEFAULT NULL COMMENT 'Opening message',
  `show_others` tinyint DEFAULT NULL COMMENT 'Whether to show prompt to others: 1 Show, 0 Hide',
  `bot_desc` varchar(255) DEFAULT NULL COMMENT 'Bot description',
  `bot_status` tinyint DEFAULT '1' COMMENT 'Bot status: 0 Offline, 1 Under review, 2 Approved, 3 Rejected, 4 Modification under review (to be displayed)',
  `block_reason` varchar(255) DEFAULT NULL COMMENT 'Reason for review rejection',
  `hot_num` int DEFAULT '0' COMMENT 'Popularity score, customizable for sorting',
  `is_delete` tinyint DEFAULT '0' COMMENT 'Application history: 0 Not deleted, 1 Deleted',
  `show_index` tinyint DEFAULT '0' COMMENT 'Whether to display on homepage recommendation: 0 No, 1 Yes',
  `sort_hot` int DEFAULT '0' COMMENT 'Manually set hottest bot position',
  `sort_latest` int DEFAULT '0' COMMENT 'Manually set latest bot position',
  `audit_time` datetime DEFAULT NULL COMMENT 'Audit time',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `support_context` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether to support multi-turn conversation: 1 Support, 0 Not support',
  `version` int DEFAULT '1' COMMENT 'Corresponding large model version, 13, 65, unit: billion',
  `show_weight` int DEFAULT '1' COMMENT 'Homepage recommended assistant weight, larger number appears first',
  `score` int DEFAULT NULL COMMENT 'Score given after review approval',
  `client_hide` varchar(10) DEFAULT '' COMMENT 'Hide on some clients',
  `model` varchar(64) DEFAULT NULL COMMENT 'Model name',
  `opened_tool` varchar(255) DEFAULT NULL COMMENT 'Enabled tools',
  PRIMARY KEY (`id`),
  KEY `idx_bot_id` (`bot_id`),
  KEY `idx_create_time3` (`create_time`),
  KEY `uid_index` (`uid`),
  KEY `idx_bot_status` (`bot_status`,`bot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Bot market table';

SET FOREIGN_KEY_CHECKS = 1;