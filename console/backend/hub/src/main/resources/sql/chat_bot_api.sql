SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_bot_api`;
CREATE TABLE `chat_bot_api` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) NOT NULL COMMENT 'User ID',
  `bot_id` int NOT NULL COMMENT 'Assistant ID',
  `assistant_id` varchar(32) NOT NULL COMMENT 'Engineering Academy assistant ID',
  `app_id` varchar(32) DEFAULT NULL COMMENT 'APPID associated with assistant API capability',
  `api_secret` varchar(64) NOT NULL COMMENT 'API secret key',
  `api_key` varchar(64) NOT NULL COMMENT 'API key',
  `api_path` varchar(32) NOT NULL COMMENT 'Path of assistant API capability',
  `prompt` varchar(2048) NOT NULL COMMENT 'Prompt of assistant API capability',
  `plugin_id` varchar(256) NOT NULL COMMENT 'Plugin ID, multiple separated by comma',
  `embedding_id` varchar(256) NOT NULL COMMENT 'Embedding ID, multiple separated by comma',
  `description` varchar(256) DEFAULT NULL COMMENT 'Description',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_assistant_id` (`assistant_id`),
  KEY `idx_bot_id` (`bot_id`),
  KEY `idx_uid` (`uid`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Assistant API capability information table';

SET FOREIGN_KEY_CHECKS = 1;