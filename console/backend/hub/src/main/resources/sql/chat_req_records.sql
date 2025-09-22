SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_req_records`;
CREATE TABLE `chat_req_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `chat_id` bigint NOT NULL COMMENT 'Chat ID',
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `message` text DEFAULT NULL COMMENT 'Question content',
  `client_type` tinyint DEFAULT '0' COMMENT 'User client type when asking: 0 Unknown, 1 PC, 2 H5 mainly for statistics',
  `model_id` int DEFAULT NULL COMMENT 'Multimodal association ID',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `date_stamp` int DEFAULT NULL COMMENT 'cmp_core.BigdataServicesMonitorDaily',
  `new_context` tinyint NOT NULL DEFAULT '1' COMMENT 'Bot new context: 1 Yes, 0 No',
  PRIMARY KEY (`id`,`create_time`),
  KEY `idx_chat_id` (`chat_id`),
  KEY `idx_create_time` (`create_time`),
  KEY `idx_date_stamp` (`date_stamp`),
  KEY `idx_uid_chatId` (`uid`,`chat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chat request record table';

SET FOREIGN_KEY_CHECKS = 1;