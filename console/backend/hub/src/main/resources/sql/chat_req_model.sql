SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS `chat_req_model`;
CREATE TABLE `chat_req_model` (
  `id` int NOT NULL AUTO_INCREMENT,
  `uid` varchar(128) NOT NULL COMMENT 'User ID',
  `chat_id` bigint DEFAULT NULL COMMENT 'Chat window ID',
  `chat_req_id` bigint NOT NULL COMMENT 'Chat request ID',
  `type` tinyint NOT NULL DEFAULT '1' COMMENT 'Multimodal type, refer to MultiModelEnum',
  `url` varchar(2048) DEFAULT NULL COMMENT 'Resource URL',
  `status` tinyint NOT NULL DEFAULT '0' COMMENT 'Review status',
  `need_his` tinyint DEFAULT '1' COMMENT 'Whether to concatenate history: 0 No, 1 Yes',
  `img_desc` varchar(2048) DEFAULT NULL COMMENT 'Image and other multimodal input description',
  `intention` varchar(255) DEFAULT NULL COMMENT 'Image intent: document document, universal natural image',
  `ocr_result` text COMMENT 'OCR recognition result',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Modification time',
  `data_id` varchar(64) DEFAULT NULL COMMENT 'Multimodal image ID, stores sseId here to identify which image for engineering institute',
  PRIMARY KEY (`id`,`create_time`),
  KEY `idx_uid` (`uid`),
  KEY `idx_req_id` (`chat_req_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='Multimodal request table';

SET FOREIGN_KEY_CHECKS = 1;