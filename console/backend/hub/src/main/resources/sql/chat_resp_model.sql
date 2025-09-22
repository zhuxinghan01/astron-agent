SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_resp_model`;
CREATE TABLE `chat_resp_model` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) NOT NULL COMMENT 'User ID',
  `chat_id` bigint DEFAULT NULL COMMENT 'Chat window ID',
  `req_id` bigint NOT NULL COMMENT 'Chat question ID, multimodal records may be stored before answers, so use reqid for association',
  `content` text DEFAULT NULL COMMENT 'Multimodal return content',
  `type` varchar(32) NOT NULL DEFAULT 'text' COMMENT 'Multimodal output type: text, image, audio, video',
  `need_his` tinyint DEFAULT '1' COMMENT 'Whether to concatenate history: 0 No, 1 Yes',
  `url` text COMMENT 'Multimodal resource URL address',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT 'Resource status: 0 Available, 1 Unavailable',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Modification time',
  `data_id` varchar(64) DEFAULT NULL COMMENT 'Large model generated resource ID, needs to be passed back for history concatenation',
  `water_url` text COMMENT 'Watermark resource URL address',
  PRIMARY KEY (`id`,`create_time`),
  KEY `idx_uid` (`uid`),
  KEY `idx_chat_id` (`chat_id`),
  KEY `idx_create_time` (`create_time`),
  KEY `idx_req_id` (`req_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Multimodal response record table';

SET FOREIGN_KEY_CHECKS = 1;