SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `bot_offiaccount_record`;
CREATE TABLE `bot_offiaccount_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bot_id` bigint DEFAULT NULL COMMENT 'Assistant ID',
  `appid` varchar(100) DEFAULT NULL COMMENT 'Official account appid',
  `auth_type` tinyint DEFAULT NULL COMMENT 'Operation type: 1 bind, 2 unbind',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `appid_index` (`appid`),
  KEY `bot_id_index` (`bot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Assistant publish operation record table';

SET FOREIGN_KEY_CHECKS = 1;