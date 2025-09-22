SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_space_permission`;
CREATE TABLE `agent_space_permission` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `module` varchar(50) DEFAULT NULL COMMENT 'Permission module',
  `point` varchar(50) DEFAULT NULL COMMENT 'Permission point',
  `description` varchar(255) DEFAULT NULL COMMENT 'Description',
  `permission_key` varchar(64) DEFAULT NULL COMMENT 'Unique permission identifier',
  `owner` tinyint NOT NULL COMMENT 'Owner (has permission): 1 yes, 0 no',
  `admin` tinyint NOT NULL COMMENT 'Administrator (has permission): 1 yes, 0 no',
  `member` tinyint NOT NULL COMMENT 'Member (has permission): 1 yes, 0 no',
  `available_expired` tinyint NOT NULL COMMENT 'Available when expired: 1 yes, 0 no',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `key_uni_key` (`permission_key`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Space role permission configuration';

SET FOREIGN_KEY_CHECKS = 1;