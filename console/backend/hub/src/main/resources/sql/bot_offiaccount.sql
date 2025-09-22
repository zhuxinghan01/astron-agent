SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `bot_offiaccount`;
CREATE TABLE `bot_offiaccount` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `bot_id` bigint DEFAULT NULL COMMENT 'Assistant ID',
  `appid` varchar(100) DEFAULT NULL COMMENT 'WeChat official account appid',
  `release_type` tinyint DEFAULT '1' COMMENT 'Release type: 1 WeChat official account',
  `status` tinyint DEFAULT '0' COMMENT 'Binding status: 0-not bound, 1-bound, 2-unbound',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `bot_id_index` (`bot_id`),
  KEY `uid_index` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Assistant and official account binding information';

SET FOREIGN_KEY_CHECKS = 1;