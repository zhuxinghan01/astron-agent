SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `user_info`;
CREATE TABLE `user_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Non-business primary key',
  `uid` varchar(255) NOT NULL COMMENT 'UID',
  `username` varchar(255) DEFAULT NULL COMMENT 'Username',
  `avatar` varchar(512) DEFAULT NULL COMMENT 'Avatar',
  `nickname` varchar(255) DEFAULT NULL COMMENT 'User nickname',
  `mobile` varchar(255) DEFAULT NULL COMMENT 'Mobile number',
  `account_status` tinyint DEFAULT '0' COMMENT 'Activation status: 0 inactive, 1 active, 2 frozen',
  `user_agreement` tinyint DEFAULT '0' COMMENT 'Whether agreed to user agreement: 0 not agreed, 1 agreed',
  `deleted` tinyint DEFAULT '0' COMMENT 'Logical deletion flag: 0 not deleted, 1 deleted',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid_unique_index` (`uid`),
  KEY `idx_create_time` (`create_time`),
  KEY `index_mobile` (`mobile`),
  KEY `idx_username` (`username`),
  KEY `idx_nickname` (`nickname`),
  KEY `idx_deleted` (`deleted`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User information table';

SET FOREIGN_KEY_CHECKS = 1;