SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_resp_alltool_data`;
CREATE TABLE `chat_resp_alltool_data` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `chat_id` bigint DEFAULT NULL COMMENT 'Chat ID',
  `req_id` bigint DEFAULT NULL COMMENT 'Request ID',
  `seq_no` varchar(100) DEFAULT NULL COMMENT 'Sequence number, like p1, p2',
  `tool_data` text COMMENT 'Structured data returned by each frame that alltools needs to store in database',
  `tool_name` varchar(100) DEFAULT NULL COMMENT 'Alltools type name',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`),
  KEY `chat_resp_alltool_data_uid_IDX` (`uid`) USING BTREE,
  KEY `chat_resp_alltool_data_chat_id_IDX` (`chat_id`) USING BTREE,
  KEY `chat_resp_alltool_data_req_id_IDX` (`req_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Large model returns alltools segment data, one Q&A returns multiple alltools segment data';

SET FOREIGN_KEY_CHECKS = 1;