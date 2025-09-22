SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_enterprise_permission`;
CREATE TABLE `agent_enterprise_permission` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `module` varchar(50) DEFAULT NULL COMMENT 'Permission module',
  `description` varchar(255) DEFAULT NULL COMMENT 'Description',
  `permission_key` varchar(64) DEFAULT NULL COMMENT 'Unique permission identifier',
  `officer` tinyint NOT NULL COMMENT 'Super administrator (has permission): 1 yes, 0 no',
  `governor` tinyint NOT NULL COMMENT 'Administrator (has permission): 1 yes, 0 no',
  `staff` tinyint NOT NULL COMMENT 'Member (has permission): 1 yes, 0 no',
  `available_expired` tinyint NOT NULL COMMENT 'Available when expired: 1 yes, 0 no',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `key_uni_key` (`permission_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Enterprise team role permission configuration';

SET FOREIGN_KEY_CHECKS = 1;