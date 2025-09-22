SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_invite_record`;
CREATE TABLE `agent_invite_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `type` tinyint DEFAULT NULL COMMENT 'Invitation type: 1 space, 2 team',
  `space_id` bigint DEFAULT NULL COMMENT 'Space ID',
  `enterprise_id` bigint DEFAULT NULL COMMENT 'Team ID',
  `invitee_uid` varchar(128) DEFAULT NULL COMMENT 'Invitee UID',
  `role` tinyint DEFAULT NULL COMMENT 'Join role: 1 administrator, 2 member',
  `invitee_nickname` varchar(64) DEFAULT NULL COMMENT 'Invitee nickname',
  `inviter_uid` varchar(128) DEFAULT NULL COMMENT 'Inviter UID',
  `expire_time` datetime DEFAULT NULL COMMENT 'Expiration time',
  `status` tinyint DEFAULT NULL COMMENT 'Status: 1 initial, 2 rejected, 3 joined, 4 withdrawn, 5 expired',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `invitee_id_key` (`invitee_uid`) USING BTREE,
  KEY `space_id_key` (`space_id`),
  KEY `enterprise_id_key` (`enterprise_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Invitation record';

SET FOREIGN_KEY_CHECKS = 1;