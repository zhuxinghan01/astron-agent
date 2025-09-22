SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `dataset_info`;
CREATE TABLE `dataset_info` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Dataset ID',
  `uid` varchar(128) NOT NULL COMMENT 'User ID',
  `name` varchar(128) NOT NULL COMMENT 'Dataset name',
  `description` varchar(256) DEFAULT NULL COMMENT 'Dataset description',
  `file_num` int DEFAULT NULL COMMENT 'File count',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT 'Status: -1 Deleted, 0 Unprocessed, 1 Processing, 2 Completed, 3 Failed',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_uid` (`uid`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Private dataset information table';

SET FOREIGN_KEY_CHECKS = 1;