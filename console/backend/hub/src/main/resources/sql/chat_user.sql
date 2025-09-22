SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_user`;
CREATE TABLE `chat_user` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Non-business primary key',
  `uid` varchar(128) DEFAULT NULL COMMENT 'If user is not logged in or registered, this is empty',
  `name` varchar(255) DEFAULT NULL COMMENT 'User name',
  `avatar` varchar(512) DEFAULT NULL COMMENT 'Avatar',
  `nickname` varchar(255) DEFAULT NULL COMMENT 'User nickname',
  `mobile` varchar(255) NOT NULL COMMENT 'Mobile phone number, does not verify authenticity, only checks for duplicates',
  `is_able` tinyint DEFAULT '0' COMMENT 'Activation status: 0 Active, 1 Inactive, 2 Frozen',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `user_agreement` tinyint DEFAULT '0' COMMENT 'Whether agreed to user agreement: 0 Not agreed, 1 Agreed',
  `date_stamp` int DEFAULT NULL COMMENT 'cmp_core.BigdataServicesMonitorDaily',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uid_unique_index` (`uid`),
  KEY `idx_create_time` (`create_time`),
  KEY `index_mobile` (`mobile`),
  KEY `idx_nickname` (`nickname`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='GPT user authorization information table';

SET FOREIGN_KEY_CHECKS = 1;