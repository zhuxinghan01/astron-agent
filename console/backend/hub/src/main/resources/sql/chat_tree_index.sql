SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;


DROP TABLE IF EXISTS `chat_tree_index`;
CREATE TABLE `chat_tree_index` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `root_chat_id` bigint(20) NOT NULL COMMENT 'Root conversation ID',
  `parent_chat_id` bigint(20) NOT NULL COMMENT 'Parent conversation ID',
  `child_chat_id` bigint(20) NOT NULL COMMENT 'Child conversation ID',
  `uid` varchar(128) DEFAULT NULL COMMENT 'uid',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT 'Creation time',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Update time',
  PRIMARY KEY (`id`,`create_time`),
  KEY `chat_tree_index_uid_IDX` (`uid`),
  KEY `chat_tree_index_root_chat_id_IDX` (`root_chat_id`),
  KEY `idx_child_chat_id` (`child_chat_id`)
) ENGINE=InnoDB AUTO_INCREMENT=957447429 DEFAULT CHARSET=utf8mb4 COMMENT='Conversation history tree linked list information';

SET FOREIGN_KEY_CHECKS = 1;
