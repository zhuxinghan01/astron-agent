SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `bot_offiaccount_chat`;
CREATE TABLE `bot_offiaccount_chat` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app_id` varchar(64) DEFAULT NULL COMMENT 'WeChat official account appid',
  `open_id` varchar(64) DEFAULT NULL COMMENT 'User ID who has followed the WeChat official account',
  `msg_id` bigint DEFAULT NULL COMMENT 'WeChat message ID, equivalent to req_id',
  `req` text COMMENT 'Message sent by user',
  `resp` text COMMENT 'Message returned by the large model',
  `sid` varchar(64) DEFAULT NULL COMMENT 'Session identifier',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `index_app_id` (`app_id`),
  KEY `index_open_id` (`open_id`),
  KEY `index_msg_id` (`msg_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Official account Q&A record table';

SET FOREIGN_KEY_CHECKS = 1;