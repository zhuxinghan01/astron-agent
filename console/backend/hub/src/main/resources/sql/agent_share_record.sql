SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `agent_share_record`;
CREATE TABLE `agent_share_record` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) NOT NULL COMMENT 'User ID',
  `base_id` bigint NOT NULL COMMENT 'Primary key ID of shared entity',
  `share_key` varchar(64) DEFAULT '' COMMENT 'Unique identifier for sharing',
  `share_type` tinyint DEFAULT '0' COMMENT 'Category: 0 share assistant',
  `is_act` tinyint DEFAULT '1' COMMENT 'Whether effective: 0 invalid, 1 valid',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_uid` (`uid`),
  KEY `idx_base_id` (`base_id`),
  KEY `idx_share_key` (`share_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Agent sharing record table';

SET FOREIGN_KEY_CHECKS = 1;