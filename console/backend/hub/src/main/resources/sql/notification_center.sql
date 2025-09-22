-- Notification center system database table structure
-- Creation time: 2025-09-13
-- Description: Message notification center module, supports multiple types including personal messages, broadcast messages, system notifications, etc.

-- General message table (including broadcast, personal, system, promotion, etc.)
CREATE TABLE `notifications` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'Auto-increment ID',
  `type` varchar(16) NOT NULL COMMENT 'Message type (personal, broadcast, system, promotion)',
  `title` varchar(255) NOT NULL COMMENT 'Message title',
  `body` text COMMENT 'Message content',
  `template_code` varchar(64) DEFAULT NULL COMMENT 'Template code, used for special rendering by client based on this code',
  `payload` json DEFAULT NULL COMMENT 'Message payload, JSON format, used to carry additional business data',
  `creator_uid` varchar(128) DEFAULT NULL COMMENT 'Creator ID, e.g., system administrator',
  `created_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT 'Creation time',
  `expire_at` datetime(3) DEFAULT NULL COMMENT 'Expiration time, can be used for automatic cleanup tasks',
  `meta` json DEFAULT NULL COMMENT 'Metadata, JSON format, used to store other additional information',
  PRIMARY KEY (`id`),
  KEY `idx_type_created` (`type`,`created_at` DESC),
  KEY `idx_expire` (`expire_at`),
  KEY `idx_creator` (`creator_uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='General message table';

-- Materialized messages for individual users (write-time fan-out)
CREATE TABLE `user_notifications` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'Auto-increment ID',
  `notification_id` bigint unsigned NOT NULL COMMENT 'Associated notification ID (notifications.id)',
  `receiver_uid` varchar(128) NOT NULL COMMENT 'Receiving user ID',
  `is_read` tinyint NOT NULL DEFAULT '0' COMMENT 'Whether read (0=unread, 1=read)',
  `read_at` datetime(3) DEFAULT NULL COMMENT 'Read time',
  `received_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT 'Received time',
  `extra` json DEFAULT NULL COMMENT 'Extra data, JSON format, used to store user-specific additional information',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uniq_user_notification` (`notification_id`,`receiver_uid`),
  KEY `idx_user_unread` (`receiver_uid`,`is_read`,`received_at` DESC),
  KEY `idx_notification` (`notification_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User personal message association table';

-- User read status for broadcast messages (only for broadcast type)
CREATE TABLE `user_broadcast_read` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT COMMENT 'Auto-increment ID',
  `receiver_uid` varchar(128) NOT NULL COMMENT 'User ID',
  `notification_id` bigint unsigned NOT NULL COMMENT 'Associated broadcast notification ID (notifications.id)',
  `read_at` datetime(3) NOT NULL DEFAULT CURRENT_TIMESTAMP(3) COMMENT 'Read time',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_receiver_notification` (`receiver_uid`, `notification_id`),
  KEY `idx_receiver_uid` (`receiver_uid`),
  KEY `idx_notification` (`notification_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='User broadcast message read status table';

-- Index descriptions
-- idx_type_created: Query messages by type and creation time
-- idx_expire: Used for scheduled tasks to automatically clean expired messages
-- idx_creator: Query messages by creator
-- idx_user_unread: Quickly query user unread messages, supports pagination
-- uniq_user_notification: Ensure the same message has only one record for the same user