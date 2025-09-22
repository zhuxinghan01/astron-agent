SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `dataset_file`;
CREATE TABLE `dataset_file` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'File ID',
  `dataset_id` bigint NOT NULL COMMENT 'Dataset ID',
  `dataset_index` varchar(255) DEFAULT NULL COMMENT 'Dataset ID',
  `name` varchar(128) NOT NULL COMMENT 'File name',
  `doc_type` varchar(32) NOT NULL COMMENT 'File type',
  `doc_url` varchar(2048) NOT NULL COMMENT 'File link',
  `s3_url` varchar(2048) DEFAULT NULL COMMENT 'S3 file link',
  `para_count` int DEFAULT NULL COMMENT 'Paragraph count',
  `char_count` int DEFAULT NULL COMMENT 'Character count',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT 'Status: -1 deleted, 0 unprocessed, 1 processing, 2 completed, 3 failed',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `idx_dataset_id` (`dataset_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Private dataset file table';

SET FOREIGN_KEY_CHECKS = 1;