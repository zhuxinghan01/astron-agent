SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_enterprise`;
CREATE TABLE `agent_enterprise` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) DEFAULT NULL COMMENT 'Creator ID',
  `name` varchar(50) DEFAULT NULL COMMENT 'Team name',
  `logo_url` varchar(1024) DEFAULT NULL COMMENT 'Logo URL',
  `avatar_url` varchar(1024) NOT NULL COMMENT 'Avatar URL',
  `org_id` bigint DEFAULT NULL COMMENT 'Organization ID',
  `service_type` tinyint DEFAULT NULL COMMENT 'Package type: 1 team, 2 enterprise',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `expire_time` datetime DEFAULT NULL COMMENT 'Expiration time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `deleted` tinyint DEFAULT '0' COMMENT 'Whether deleted: 0 no, 1 yes',
  PRIMARY KEY (`id`),
  KEY `enterprise_name_key` (`name`) USING BTREE,
  KEY `enterprise_uid_key` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Enterprise team';

SET FOREIGN_KEY_CHECKS = 1;