SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_space_user`;
CREATE TABLE `agent_space_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `space_id` bigint NOT NULL COMMENT 'Space ID',
  `uid` varchar(128) NOT NULL COMMENT 'User ID',
  `nickname` varchar(64) DEFAULT NULL COMMENT 'User nickname',
  `role` tinyint NOT NULL COMMENT 'Role: 1 owner, 2 administrator, 3 member',
  `last_visit_time` datetime DEFAULT NULL COMMENT 'Last visit time',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Modification time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `space_id_uid_uni_key` (`space_id`,`uid`) USING BTREE,
  KEY `space_user_uid_key` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Space user';

SET FOREIGN_KEY_CHECKS = 1;