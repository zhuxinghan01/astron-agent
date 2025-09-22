SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_file_req`;
CREATE TABLE `chat_file_req` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file_id` varchar(64) NOT NULL COMMENT 'Document Q&A fileId',
  `chat_id` bigint NOT NULL COMMENT 'Chat ID',
  `req_id` bigint DEFAULT NULL COMMENT 'req_id',
  `uid` varchar(128) NOT NULL COMMENT 'Owner uid',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `client_type` tinyint NOT NULL DEFAULT '0' COMMENT 'Client type: 0 Unknown, 1 PC, 2 H5 mainly for statistics',
  `deleted` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether deleted: 0 Not deleted, 1 Deleted',
  `business_type` tinyint NOT NULL DEFAULT '0' COMMENT 'Document type: 0 Long document, 1 Long audio, 2 Long video, 3 OCR',
  PRIMARY KEY (`id`),
  KEY `idx_chatid_uid_fileid` (`chat_id`,`uid`,`file_id`),
  KEY `idx_create_time` (`create_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chat file Q&A binding information';

SET FOREIGN_KEY_CHECKS = 1;