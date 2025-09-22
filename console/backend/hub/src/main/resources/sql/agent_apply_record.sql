SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_apply_record`;
CREATE TABLE `agent_apply_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `enterprise_id` bigint DEFAULT NULL COMMENT 'Enterprise team ID',
  `space_id` bigint DEFAULT NULL COMMENT 'Space ID',
  `apply_uid` varchar(128) DEFAULT NULL COMMENT 'Applicant UID',
  `apply_nickname` varchar(64) DEFAULT NULL COMMENT 'Applicant nickname',
  `apply_time` datetime DEFAULT NULL COMMENT 'Application time',
  `status` tinyint DEFAULT NULL COMMENT 'Application status: 1 pending confirmation, 2 approved, 3 rejected',
  `audit_time` datetime DEFAULT NULL COMMENT 'Processing time',
  `audit_uid` varchar(128) DEFAULT NULL COMMENT 'Processor UID',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `enterprise_id_key` (`enterprise_id`) USING BTREE,
  KEY `space_id_key` (`space_id`) USING BTREE,
  KEY `apply_uid_key` (`apply_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Application to join space/enterprise record';

SET FOREIGN_KEY_CHECKS = 1;