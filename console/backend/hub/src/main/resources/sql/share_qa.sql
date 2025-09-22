SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `share_qa`;
CREATE TABLE `share_qa` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) DEFAULT NULL COMMENT 'User ID',
  `share_chat_id` bigint DEFAULT NULL COMMENT 'Primary key ID corresponding to share_chat',
  `message_q` text DEFAULT NULL COMMENT 'Question content',
  `message_a` mediumtext COMMENT 'Answer content',
  `sid` varchar(128) DEFAULT NULL COMMENT 'Answer SID',
  `show_status` tinyint DEFAULT '1' COMMENT 'Whether valid: 1 Valid, 0 Invalid',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  `req_id` bigint DEFAULT NULL COMMENT 'User question, chat_req_records primary key ID',
  `req_type` tinyint DEFAULT '0' COMMENT 'Multimodal question type',
  `req_url` text COMMENT 'Multimodal question URL',
  `resp_id` bigint DEFAULT '0' COMMENT 'Answer table primary key ID',
  `resp_type` varchar(128) DEFAULT NULL COMMENT 'Multimodal response type',
  `resp_url` varchar(512) DEFAULT NULL COMMENT 'Multimodal response URL',
  `chat_key` varchar(64) DEFAULT NULL COMMENT 'Identifier for direct conversation on share page, same function as chatId',
  PRIMARY KEY (`id`),
  KEY `uin_uid_share-chat-id` (`uid`,`share_chat_id`),
  KEY `idx_uid` (`uid`),
  KEY `idx_resp_type` (`resp_type`),
  KEY `idx_share_chat_id` (`share_chat_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Conversation share Q&A content table';

SET FOREIGN_KEY_CHECKS = 1;