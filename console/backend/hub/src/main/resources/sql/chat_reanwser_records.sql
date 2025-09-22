SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_reanwser_records`;
CREATE TABLE `chat_reanwser_records` (
  `id` bigint NOT NULL AUTO_INCREMENT COMMENT 'Non-business primary key',
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `chat_id` bigint DEFAULT NULL COMMENT 'Chat ID',
  `req_id` bigint DEFAULT NULL COMMENT 'Request ID before regeneration, for locating historical context position',
  `ask` varchar(8000) DEFAULT NULL COMMENT 'Prompt content',
  `answer` varchar(8000) DEFAULT NULL COMMENT 'Reply content',
  `ask_time` datetime DEFAULT NULL COMMENT 'Question record time',
  `answer_time` datetime DEFAULT NULL COMMENT 'Answer record time',
  `sid` varchar(64) DEFAULT NULL COMMENT 'Reply SID',
  `answer_type` tinyint DEFAULT NULL COMMENT 'Reply type: 0 System, 1 Quick fix (API interface not used), 2 Large model, 3 Stop',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`,`create_time`),
  KEY `uid_index` (`uid`),
  KEY `chat_index` (`chat_id`),
  KEY `idx_sid` (`sid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Chat regeneration record table';

SET FOREIGN_KEY_CHECKS = 1;