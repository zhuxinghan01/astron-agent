SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_space`;
CREATE TABLE `agent_space` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(50) NOT NULL COMMENT 'Space name',
  `description` varchar(2000) DEFAULT NULL COMMENT 'Description',
  `avatar_url` varchar(1024) DEFAULT NULL COMMENT 'Avatar URL',
  `uid` varchar(128) DEFAULT NULL COMMENT 'Creator ID',
  `enterprise_id` bigint DEFAULT NULL COMMENT 'Team ID',
  `type` tinyint DEFAULT NULL COMMENT 'Type: 1 free version, 2 professional version, 3 team version, 4 enterprise version',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `deleted` tinyint DEFAULT '0' COMMENT 'Whether deleted: 0 no, 1 yes',
  PRIMARY KEY (`id`),
  KEY `uid_key` (`uid`),
  KEY `enterprise_id_key` (`enterprise_id`) USING BTREE,
  KEY `space_name` (`name`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Space';

SET FOREIGN_KEY_CHECKS = 1;