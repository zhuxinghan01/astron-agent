SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_resp_records`;
CREATE TABLE `chat_resp_records` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `chat_id` bigint DEFAULT NULL COMMENT 'Chat ID',
  `req_id` bigint DEFAULT NULL COMMENT 'Chat question ID, one question to one answer',
  `sid` varchar(128) DEFAULT NULL COMMENT 'Engine serial number sid',
  `answer_type` tinyint DEFAULT '2' COMMENT 'Answer type: 1 hotfix, 2 gpt',
  `message` mediumtext COMMENT 'Answer message',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `date_stamp` int DEFAULT NULL COMMENT 'cmp_core.BigdataServicesMonitorDaily',
  PRIMARY KEY (`id`,`create_time`),
  KEY `idx_chat_id` (`chat_id`),
  KEY `idx_create_time` (`create_time`),
  KEY `idx_reqId` (`req_id`),
  KEY `idx_sid` (`sid`),
  KEY `idx_uid_chatId` (`uid`,`chat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chat response record table';

SET FOREIGN_KEY_CHECKS = 1;