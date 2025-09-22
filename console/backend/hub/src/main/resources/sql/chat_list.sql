SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_list`;
CREATE TABLE `chat_list` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Non-business primary key',
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `title` varchar(255) DEFAULT NULL COMMENT 'Chat list title',
  `is_delete` tinyint DEFAULT '0' COMMENT 'Whether deleted: 0 Not deleted, 1 Deleted',
  `enable` tinyint DEFAULT '1' COMMENT 'Enable status: 1 Available, 0 Unavailable',
  `bot_id` int DEFAULT '0' COMMENT 'Assistant ID',
  `sticky` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether sticky: 0 Not sticky, 1 Sticky',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Modification time',
  `is_model` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether multimodal: 0 No, 1 Yes',
  `enabled_plugin_ids` varchar(255) DEFAULT '' COMMENT 'Enabled plugin IDs for current chat list',
  `is_botweb` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether it is an assistant WEB application: 0 No, 1 Yes',
  `file_id` varchar(64) DEFAULT NULL COMMENT 'Document Q&A ID',
  `root_flag` tinyint NOT NULL DEFAULT '1' COMMENT 'Whether it is a root chat: 1 Yes, 0 No',
  `personality_id` bigint DEFAULT '0' COMMENT 'Personality chat_personality_base primary key ID',
  `gcl_id` bigint DEFAULT '0' COMMENT 'Group chat primary key ID, 0 means not group chat',
  PRIMARY KEY (`id`,`create_time`),
  KEY `chat_list_create_time_IDX` (`create_time`),
  KEY `idx_bot_id` (`bot_id`),
  KEY `idx_uid_bid_ctime` (`uid`,`bot_id`,`create_time`),
  KEY `chat_list_file_id_idx` (`file_id`),
  KEY `idx_pid_uid` (`personality_id`,`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chat list table';

SET FOREIGN_KEY_CHECKS = 1;