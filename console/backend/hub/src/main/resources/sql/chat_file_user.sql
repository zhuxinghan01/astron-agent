SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_file_user`;
CREATE TABLE `chat_file_user` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `file_id` varchar(64) DEFAULT NULL COMMENT 'Document Q&A fileId',
  `uid` varchar(128) NOT NULL COMMENT 'Owner uid',
  `file_url` varchar(1024) DEFAULT NULL COMMENT 'File URL',
  `file_name` varchar(128) DEFAULT NULL COMMENT 'File name',
  `file_size` bigint DEFAULT NULL COMMENT 'File size',
  `file_pdf_url` varchar(1024) DEFAULT NULL COMMENT 'File PDF URL',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `deleted` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether deleted: 0 Not deleted, 1 Deleted',
  `client_type` tinyint NOT NULL DEFAULT '0' COMMENT 'Client type: 0 Unknown, 1 PC, 2 H5 mainly for statistics',
  `business_type` tinyint NOT NULL DEFAULT '0' COMMENT 'Document type: 0 Long document, 1 Long audio, 2 Long video, 3 OCR',
  `display` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether to display in history knowledge base: 0 Display, 1 Not display',
  `file_status` tinyint NOT NULL DEFAULT '1' COMMENT 'Document status: 0 Unprocessed, 1 Processing, 2 Completed, 3 Failed',
  `file_business_key` varchar(1024) DEFAULT NULL COMMENT 'Unique file key maintained by frontend',
  `extra_link` varchar(1024) DEFAULT NULL COMMENT 'Video external link processing',
  `document_type` tinyint DEFAULT '1' COMMENT 'Document classification: 1 Spark Document, 2 Zhiwen, see light_app_detail.additional_info field',
  `file_index` int DEFAULT NULL COMMENT 'Daily upload count per user',
  `scene_type_id` bigint DEFAULT NULL COMMENT 'File scenario: related to document_scene_type table',
  `icon` varchar(1024) DEFAULT NULL COMMENT 'Favorites icon display',
  `collect_origin_from` varchar(1024) DEFAULT NULL COMMENT 'Favorites content source',
  `task_id` varchar(100) DEFAULT NULL COMMENT 'RAG-v2 version task ID',
  PRIMARY KEY (`id`),
  KEY `chat_file_user_file_id_IDX` (`file_id`) USING BTREE,
  KEY `chat_file_user_uid_IDX` (`uid`) USING BTREE,
  KEY `chat_file_user_create_time_IDX` (`create_time`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='User file information';

SET FOREIGN_KEY_CHECKS = 1;