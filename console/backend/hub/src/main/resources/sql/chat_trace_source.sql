SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_trace_source`;
CREATE TABLE `chat_trace_source` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `chat_id` bigint DEFAULT NULL COMMENT 'Chat ID',
  `req_id` bigint DEFAULT NULL COMMENT 'Request ID',
  `content` text COMMENT 'Trace source content, one frame JSON array',
  `type` varchar(50) DEFAULT 'search' COMMENT 'Trace source type: search source tracing, others supplement',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `chat_trace_source_chat_id_IDX` (`chat_id`) USING BTREE,
  KEY `chat_trace_source_type_IDX` (`type`) USING BTREE,
  KEY `chat_trace_source_uid_IDX` (`uid`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chat trace source information storage table';

SET FOREIGN_KEY_CHECKS = 1;