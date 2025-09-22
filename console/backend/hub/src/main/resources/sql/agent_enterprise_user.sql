SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_enterprise_user`;
CREATE TABLE `agent_enterprise_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `enterprise_id` bigint DEFAULT NULL COMMENT 'Team ID',
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `nickname` varchar(64) DEFAULT NULL COMMENT 'User nickname',
  `role` tinyint DEFAULT NULL COMMENT 'Role: 1 super administrator, 2 administrator, 3 member',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `enterprise_id_uid_uni_key` (`enterprise_id`,`uid`) USING BTREE,
  KEY `enterprise_user_uid_key` (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Enterprise team user';

SET FOREIGN_KEY_CHECKS = 1;