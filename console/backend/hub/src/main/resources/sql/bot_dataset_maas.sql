SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `bot_dataset_maas`;
CREATE TABLE `bot_dataset_maas` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `bot_id` bigint NOT NULL COMMENT 'Corresponding to chat_bot_base table primary key id',
  `dataset_id` bigint DEFAULT NULL COMMENT 'Primary key id of dataset_info table',
  `dataset_index` varchar(255) DEFAULT NULL COMMENT 'Dataset ID of knowledge database',
  `is_act` tinyint DEFAULT '1' COMMENT 'Whether effective: 0 not effective, 1 effective, 2 under review after market update',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  PRIMARY KEY (`id`),
  UNIQUE KEY `idx_id_bot_id` (`id`,`bot_id`),
  KEY `idx_uid` (`uid`),
  KEY `idx_is_act` (`is_act`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Assistant associated MAAS dataset index table';

SET FOREIGN_KEY_CHECKS = 1;