-- global
SET GLOBAL character_set_client = utf8mb4;
SET GLOBAL character_set_connection = utf8mb4;
SET GLOBAL character_set_results = utf8mb4;
SET GLOBAL collation_connection = utf8mb4_general_ci;

-- casdoor database init

CREATE DATABASE IF NOT EXISTS casdoor COLLATE utf8mb4_general_ci;

-- rpa database init

CREATE DATABASE IF NOT EXISTS rpa COLLATE utf8mb4_general_ci;

USE rpa;
-- rpa.alarm_rule definition

CREATE TABLE `alarm_rule` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `enable` tinyint(3) DEFAULT NULL COMMENT '是否启用',
  `name` varchar(255) DEFAULT NULL COMMENT '规则名',
  `condition` varchar(100) DEFAULT NULL COMMENT '条件JSON字符串：{"hours":23,"minutes":59,"count":10}',
  `duration` char(17) DEFAULT NULL COMMENT 'HH:MM:SS-HH:MM:SS  时间段（开始-结束）',
  `role_id` char(36) DEFAULT NULL COMMENT '操作者角色id',
  `process_id_list` mediumtext COMMENT 'processId',
  `event_module_code` int(11) DEFAULT NULL COMMENT '事件模块代码',
  `event_module_name` varchar(255) DEFAULT NULL COMMENT '事件模块',
  `event_type_code` int(11) DEFAULT NULL COMMENT '事件代码',
  `event_type_name` varchar(255) DEFAULT NULL COMMENT '事件类型',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(6) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1966060594098135041 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.alarm_rule_user definition

CREATE TABLE `alarm_rule_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `alarm_rule_id` bigint(20) DEFAULT NULL COMMENT 'alarm_rule表id',
  `phone` varchar(200) DEFAULT NULL COMMENT '电话',
  `name` varchar(100) DEFAULT NULL COMMENT '用户姓名',
  `deleted` smallint(6) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1966061018251321345 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.app_application definition

CREATE TABLE `app_application` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `robot_id` varchar(100) NOT NULL COMMENT '机器人ID',
  `robot_version` int(11) NOT NULL COMMENT '机器人版本ID',
  `status` varchar(20) NOT NULL COMMENT '状态: 待审核pending, 已通过approved, 未通过rejected, 已撤销canceled，作废nullify',
  `application_type` varchar(20) NOT NULL COMMENT '申请类型: release(上架)/use(使用)',
  `security_level` varchar(10) DEFAULT NULL COMMENT '审核设置的密级red,green,yellow',
  `allowed_dept` varchar(5000) DEFAULT NULL COMMENT '允许使用的部门ID列表',
  `expire_time` timestamp NULL DEFAULT NULL COMMENT '使用期限(截止日期)',
  `audit_opinion` varchar(500) DEFAULT NULL COMMENT '审核意见',
  `creator_id` char(36) DEFAULT NULL COMMENT '申请人ID',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者或审核者id',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted` smallint(1) DEFAULT '0',
  `tenant_id` char(36) CHARACTER SET utf8 DEFAULT NULL,
  `client_deleted` smallint(1) DEFAULT '0' COMMENT '客户端的申请记录-是否删除',
  `cloud_deleted` smallint(1) DEFAULT '0' COMMENT '卓越中心的申请记录-是否删除',
  `default_pass` smallint(1) DEFAULT NULL COMMENT '选择绿色密级时，后续更新发版是否默认通过',
  `market_info` varchar(500) DEFAULT NULL COMMENT '团队市场id等信息，用于第一次发起上架申请，审核通过后自动分享到该市场',
  `publish_info` varchar(500) DEFAULT NULL COMMENT '发版JSON信息',
  PRIMARY KEY (`id`),
  KEY `idx_app_robot` (`robot_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1967839071050592259 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='上架/使用审核表';


-- rpa.app_application_tenant definition

CREATE TABLE `app_application_tenant` (
  `tenant_id` varchar(36) NOT NULL,
  `audit_enable` smallint(6) DEFAULT NULL COMMENT '是否开启审核，1开启，0不开启',
  `audit_enable_time` timestamp NULL DEFAULT NULL,
  `audit_enable_operator` char(36) DEFAULT NULL,
  `audit_enable_reason` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`tenant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='租户是否开启审核配置表';


-- rpa.app_market definition

CREATE TABLE `app_market` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) DEFAULT NULL,
  `market_id` varchar(20) DEFAULT NULL COMMENT '团队市场id',
  `market_name` varchar(60) DEFAULT NULL COMMENT '市场名称',
  `market_describe` varchar(800) DEFAULT NULL COMMENT '市场描述',
  `market_type` varchar(10) DEFAULT NULL COMMENT '市场类型：team,official',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`),
  KEY `app_market_creator_id_IDX` (`creator_id`),
  KEY `app_market_market_id_IDX` (`market_id`),
  KEY `app_market_tenant_id_IDX` (`tenant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=134 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='团队市场-团队表';


-- rpa.app_market_dict definition

CREATE TABLE `app_market_dict` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `business_code` varchar(100) DEFAULT NULL COMMENT '业务编码：1、行业类型，2、角色功能marketRoleFunc',
  `name` varchar(64) DEFAULT NULL COMMENT '行业名称，角色功能名称',
  `dict_code` varchar(64) DEFAULT NULL COMMENT '行业编码，功能编码',
  `dict_value` varchar(100) DEFAULT NULL COMMENT 'T有权限，F无权限',
  `user_type` varchar(100) DEFAULT NULL COMMENT 'owner,admin,acquirer,author',
  `description` varchar(256) DEFAULT NULL COMMENT '描述',
  `seq` int(11) DEFAULT NULL COMMENT '排序',
  `creator_id` char(36) DEFAULT '73',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` char(36) DEFAULT '73',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` smallint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `app_market_dict_dict_code_IDX` (`dict_code`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=80 DEFAULT CHARSET=utf8;


-- rpa.app_market_resource definition

CREATE TABLE `app_market_resource` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `market_id` varchar(20) DEFAULT NULL COMMENT '团队市场id',
  `app_id` varchar(50) DEFAULT NULL COMMENT '应用id，模板id，组件id',
  `download_num` bigint(20) DEFAULT '0' COMMENT '下载次数',
  `check_num` bigint(20) DEFAULT '0' COMMENT '查看次数',
  `creator_id` char(36) DEFAULT NULL COMMENT '发布人',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  `robot_id` varchar(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '机器人id',
  `app_name` varchar(64) CHARACTER SET utf8 DEFAULT NULL COMMENT '资源名称',
  PRIMARY KEY (`id`),
  KEY `app_market_resource_app_id_IDX` (`app_id`),
  KEY `app_market_resource_creator_id_IDX` (`creator_id`),
  KEY `app_market_resource_market_id_IDX` (`market_id`),
  KEY `app_market_resource_tenant_id_IDX` (`tenant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=196 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='团队市场-资源映射表';


-- rpa.app_market_user definition

CREATE TABLE `app_market_user` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) DEFAULT NULL COMMENT '根据id找在对应租户的信息',
  `market_id` varchar(20) DEFAULT NULL COMMENT '团队市场id',
  `user_type` varchar(10) DEFAULT NULL COMMENT '成员类型：owner,admin,acquirer,author',
  `creator_id` char(36) DEFAULT NULL COMMENT '成员id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '加入时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`),
  KEY `app_market_user_creator_id_IDX` (`creator_id`),
  KEY `app_market_user_market_id_IDX` (`market_id`),
  KEY `app_market_user_tenant_id_IDX` (`tenant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=201 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='团队市场-人员表，n:n的关系';


-- rpa.app_market_version definition

CREATE TABLE `app_market_version` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `market_id` varchar(100) DEFAULT NULL COMMENT '团队市场id',
  `app_id` varchar(50) DEFAULT NULL,
  `app_version` int(11) DEFAULT NULL COMMENT '应用版本，同机器人版本',
  `edit_flag` tinyint(1) DEFAULT '1' COMMENT '自己创建的分享到市场，是否支持编辑/开放源码；0不支持，1支持',
  `category` varchar(100) DEFAULT NULL COMMENT '分享到市场的机器人行业：政务、医疗、商业等',
  `creator_id` char(36) DEFAULT NULL COMMENT '发布人',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发布时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `app_market_version_app_id_IDX` (`app_id`) USING BTREE,
  KEY `app_market_version_market_id_IDX` (`market_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=280 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='团队市场-应用版本表';


-- rpa.atom_like definition

CREATE TABLE `atom_like` (
  `id` int(20) NOT NULL AUTO_INCREMENT,
  `like_id` varchar(20) NOT NULL,
  `atom_key` varchar(100) NOT NULL COMMENT '原子能力的key，全局唯一',
  `creator_id` char(36) NOT NULL,
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `is_deleted` smallint(1) NOT NULL DEFAULT '0',
  `updater_id` char(36) DEFAULT NULL,
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8 COMMENT='原子能力收藏';


-- rpa.atom_meta_duplicate_log definition

CREATE TABLE `atom_meta_duplicate_log` (
  `id` bigint(20) NOT NULL DEFAULT '0',
  `atom_key` varchar(100) DEFAULT NULL,
  `version` varchar(20) DEFAULT NULL COMMENT '原子能力版本',
  `request_body` mediumtext COMMENT '完整请求体',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除',
  `creator_id` bigint(20) DEFAULT '73',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` bigint(20) DEFAULT '73',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.audit_checkpoint definition

CREATE TABLE `audit_checkpoint` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `audit_object_type` varchar(36) DEFAULT NULL COMMENT 'robot，dept',
  `last_processed_id` varchar(36) DEFAULT NULL,
  `audit_status` varchar(20) DEFAULT NULL COMMENT '统计进度：counting, completed, pending,to_count',
  `count_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '删除标识',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=324 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='监控管理统计断点表';


-- rpa.audit_record definition

CREATE TABLE `audit_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `event_module_code` int(11) DEFAULT NULL COMMENT '事件模块代码',
  `event_module_name` varchar(255) DEFAULT NULL COMMENT '事件模块',
  `event_type_code` int(11) DEFAULT NULL COMMENT '事件代码',
  `event_type_name` varchar(255) DEFAULT NULL COMMENT '事件类型',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `creator_name` varchar(255) DEFAULT NULL COMMENT '创建者名称',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '创建时间',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `event_detail` varchar(255) DEFAULT NULL COMMENT '事件详情',
  `process_id_list` mediumtext COMMENT 'processId',
  `role_id_list` mediumtext COMMENT '角色id列表',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=150 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.c_atom_meta definition

CREATE TABLE `c_atom_meta` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `parent_key` varchar(100) DEFAULT NULL,
  `atom_key` varchar(100) DEFAULT NULL,
  `atom_content` mediumtext COMMENT '原子能力所有配置信息，json',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除',
  `creator_id` char(36) DEFAULT '73',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` bigint(20) DEFAULT '73',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `version` varchar(20) DEFAULT NULL COMMENT '原子能力版本',
  `sort` int(11) DEFAULT NULL COMMENT '原子能力展示顺序',
  `version_num` varchar(100) DEFAULT NULL COMMENT '大版本',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=274 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.c_element definition

CREATE TABLE `c_element` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `element_id` varchar(100) DEFAULT NULL COMMENT '元素id',
  `element_name` varchar(100) DEFAULT NULL COMMENT '元素名称',
  `icon` varchar(100) DEFAULT NULL COMMENT '图标',
  `image_id` varchar(100) DEFAULT NULL COMMENT '图片下载地址',
  `parent_image_id` varchar(100) DEFAULT NULL COMMENT '元素的父级图片下载地址',
  `element_data` mediumtext COMMENT '元素内容',
  `deleted` smallint(6) DEFAULT '0',
  `creator_id` char(36) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` char(36) DEFAULT NULL,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `robot_id` varchar(100) DEFAULT NULL,
  `robot_version` int(11) DEFAULT NULL,
  `group_id` varchar(30) DEFAULT NULL,
  `common_sub_type` varchar(50) DEFAULT NULL COMMENT 'cv图像, sigle普通拾取，batch数据抓取',
  `group_name` varchar(100) DEFAULT NULL,
  `element_type` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6205 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='客户端，元素信息';


-- rpa.c_global_var definition

CREATE TABLE `c_global_var` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `project_id` varchar(100) DEFAULT NULL,
  `global_id` varchar(100) DEFAULT NULL,
  `var_name` varchar(100) DEFAULT NULL,
  `var_type` varchar(100) DEFAULT NULL,
  `var_value` varchar(100) DEFAULT NULL,
  `var_describe` varchar(100) DEFAULT NULL,
  `deleted` smallint(6) DEFAULT NULL,
  `creator_id` char(36) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` char(36) DEFAULT NULL,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `robot_id` varchar(100) DEFAULT NULL,
  `robot_version` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=506 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='客户端-全局变量';


-- rpa.c_group definition

CREATE TABLE `c_group` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `group_id` varchar(100) DEFAULT NULL,
  `group_name` varchar(100) DEFAULT NULL,
  `creator_id` char(36) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` char(36) DEFAULT NULL,
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `deleted` smallint(6) DEFAULT '0',
  `robot_id` varchar(100) DEFAULT NULL,
  `robot_version` int(11) DEFAULT NULL,
  `element_type` varchar(20) DEFAULT NULL COMMENT 'cv：cv拾取; common:普通元素拾取',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1505 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='元素或图像的分组';


-- rpa.c_module definition

CREATE TABLE `c_module` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `module_id` varchar(100) DEFAULT NULL COMMENT '流程id',
  `module_content` mediumtext COMMENT '全量python代码数据',
  `module_name` varchar(100) DEFAULT NULL COMMENT 'python文件名',
  `deleted` smallint(6) DEFAULT '0',
  `creator_id` char(36) DEFAULT '73',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` char(36) DEFAULT '73',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `robot_id` varchar(100) DEFAULT NULL,
  `robot_version` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=285 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='客户端-python模块数据';


-- rpa.c_param definition

CREATE TABLE `c_param` (
  `id` varchar(20) NOT NULL COMMENT '参数id',
  `var_direction` int(11) DEFAULT NULL COMMENT '输入/输出',
  `var_name` varchar(100) DEFAULT NULL COMMENT '参数名称',
  `var_type` varchar(100) DEFAULT NULL COMMENT '参数类型',
  `var_value` varchar(100) DEFAULT NULL COMMENT '参数内容',
  `var_describe` varchar(100) DEFAULT NULL COMMENT '参数描述',
  `process_id` varchar(100) DEFAULT NULL COMMENT '流程id',
  `creator_id` char(36) DEFAULT NULL,
  `updater_id` char(36) DEFAULT NULL,
  `create_time` timestamp NULL DEFAULT NULL,
  `update_time` timestamp NULL DEFAULT NULL,
  `deleted` int(11) DEFAULT NULL,
  `robot_id` varchar(100) DEFAULT NULL,
  `robot_version` int(11) DEFAULT NULL,
  KEY `c_param_id_IDX` (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.c_process definition

CREATE TABLE `c_process` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `project_id` varchar(100) DEFAULT NULL COMMENT '工程id',
  `process_id` varchar(100) DEFAULT NULL COMMENT '流程id',
  `process_content` mediumtext COMMENT '全量流程数据',
  `process_name` varchar(100) DEFAULT NULL COMMENT '流程名称',
  `deleted` smallint(6) DEFAULT '0',
  `creator_id` char(36) DEFAULT '73',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updater_id` char(36) DEFAULT '73',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `robot_id` varchar(100) DEFAULT NULL,
  `robot_version` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3568 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='客户端-流程数据';


-- rpa.c_project definition

CREATE TABLE `c_project` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `project_id` varchar(100) DEFAULT NULL,
  `project_name` varchar(200) CHARACTER SET utf8 DEFAULT NULL COMMENT '项目名称',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` datetime DEFAULT NULL COMMENT '创建时间',
  `deleted` tinyint(1) DEFAULT '0' COMMENT '逻辑删除 0：未删除 1：已删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='工程表';


-- rpa.c_require definition

CREATE TABLE `c_require` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `project_id` varchar(100) DEFAULT NULL,
  `package_name` varchar(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '项目名称',
  `package_version` varchar(20) DEFAULT NULL,
  `mirror` varchar(100) DEFAULT NULL,
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` datetime DEFAULT NULL COMMENT '创建时间',
  `deleted` tinyint(1) DEFAULT '0' COMMENT '逻辑删除 0：未删除 1：已删除',
  `robot_id` varchar(100) DEFAULT NULL,
  `robot_version` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=116 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='python依赖管理';


-- rpa.cloud_terminal definition

CREATE TABLE `cloud_terminal` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `dept_id_path` varchar(100) DEFAULT NULL COMMENT '部门全路径id',
  `name` varchar(100) DEFAULT NULL COMMENT '终端名称',
  `terminal_mac` varchar(100) DEFAULT NULL COMMENT '设备号，终端唯一标识',
  `terminal_ip` varchar(100) DEFAULT NULL COMMENT 'ip',
  `terminal_status` varchar(100) DEFAULT NULL COMMENT '当前状态，忙碌busy，空闲free，离线offline',
  `terminal_des` varchar(100) DEFAULT NULL COMMENT '终端描述',
  `user_id` char(36) DEFAULT NULL COMMENT '最近登陆用户id',
  `dept_name` varchar(100) DEFAULT NULL COMMENT '部门名称',
  `account_last` varchar(100) DEFAULT NULL COMMENT '最近登陆账号',
  `user_name_last` varchar(100) DEFAULT NULL COMMENT '最近登陆用户名',
  `time_last` timestamp NULL DEFAULT NULL COMMENT '最近登陆时间',
  `execute_time_total` bigint(20) DEFAULT '0' COMMENT '单个终端累计执行时长，用于终端列表展示，更新机器人执行记录表时同步更新该表',
  `execute_num` bigint(20) DEFAULT '0' COMMENT '单个终端累计执行次数，更新机器人执行记录表时同步更新该表',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '终端记录创建时间',
  `terminal_type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `cloud_terminal_mac_tenant_index` (`terminal_mac`,`tenant_id`),
  KEY `cloud_terminal_tenant_id_IDX` (`tenant_id`,`dept_id_path`),
  KEY `cloud_terminal_terminal_mac_IDX` (`terminal_mac`),
  KEY `cloud_terminal_user_id_IDX` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='终端表';


-- rpa.component definition

CREATE TABLE `component` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `component_id` varchar(100) NOT NULL COMMENT '机器人唯一id，获取的应用id',
  `name` varchar(100) NOT NULL COMMENT '当前名字，用于列表展示',
  `creator_id` char(36) NOT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) NOT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `is_shown` smallint(1) NOT NULL DEFAULT '1' COMMENT '是否在用户列表页显示 0：不显示，1：显示',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  `app_id` varchar(50) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT 'appmarketResource中的应用id',
  `app_version` int(11) DEFAULT NULL COMMENT '获取的应用：应用市场版本',
  `market_id` varchar(20) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '获取的应用：市场id',
  `resource_status` varchar(20) DEFAULT NULL COMMENT '资源状态：toObtain, obtained, toUpdate',
  `data_source` varchar(20) DEFAULT NULL COMMENT '来源：create 自己创建 ； market 市场获取 ',
  `transform_status` varchar(20) DEFAULT NULL COMMENT 'editing 编辑中，published 已发版，shared 已上架，locked锁定（无法编辑）',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8 COMMENT='组件表';


-- rpa.component_robot_block definition

CREATE TABLE `component_robot_block` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `robot_id` varchar(100) CHARACTER SET utf8 NOT NULL COMMENT '机器人id',
  `robot_version` int(10) NOT NULL COMMENT '机器人版本号',
  `component_id` varchar(100) CHARACTER SET utf8 NOT NULL COMMENT '组件id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='机器人对组件屏蔽表';


-- rpa.component_robot_use definition

CREATE TABLE `component_robot_use` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `robot_id` varchar(100) CHARACTER SET utf8 NOT NULL COMMENT '机器人id',
  `robot_version` int(10) NOT NULL COMMENT '机器人版本号',
  `component_id` varchar(100) CHARACTER SET utf8 NOT NULL COMMENT '组件id',
  `component_version` int(10) NOT NULL COMMENT '组件版本号',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='机器人对组件引用表';


-- rpa.component_version definition

CREATE TABLE `component_version` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `component_id` varchar(100) CHARACTER SET utf8 NOT NULL COMMENT '机器人id',
  `version` int(10) NOT NULL COMMENT '版本号',
  `introduction` longtext CHARACTER SET utf8 COMMENT '简介',
  `update_log` longtext CHARACTER SET utf8 COMMENT '更新日志',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  `param` text CHARACTER SET utf8,
  `param_detail` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '发版时拖的表单参数信息',
  `icon` varchar(30) NOT NULL COMMENT '图标',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=68 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='组件版本表';


-- rpa.dispatch_day_task_info definition

CREATE TABLE `dispatch_day_task_info` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `terminal_id` varchar(20) DEFAULT NULL COMMENT '终端id',
  `task_id` varchar(30) DEFAULT NULL COMMENT '任务ID',
  `task_name` varchar(30) DEFAULT NULL COMMENT '任务名',
  `robot_id` varchar(30) DEFAULT NULL COMMENT '机器人ID',
  `robot_name` varchar(30) DEFAULT NULL COMMENT '机器人名',
  `status` varchar(10) DEFAULT NULL COMMENT '当前状态 待执行 todo /已执行 done /在执行 doing',
  `execute_time` varchar(10) DEFAULT NULL COMMENT '任务执行时间',
  `sort` int(11) DEFAULT NULL COMMENT '排序, 越小越靠前',
  `tenant_id` bigint(20) DEFAULT NULL,
  `creator_id` bigint(20) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` bigint(20) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_task_id` (`task_id`),
  KEY `idx_robot_id` (`robot_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='调度模式:终端每日上传的任务情况信息';


-- rpa.dispatch_task definition

CREATE TABLE `dispatch_task` (
  `dispatch_task_id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '调度模式计划任务id',
  `status` varchar(10) NOT NULL DEFAULT '0' COMMENT '任务状态：启用中active、关闭stop、已过期expired',
  `name` varchar(50) DEFAULT NULL COMMENT '调度模式计划任务名称',
  `cron_json` mediumtext COMMENT '构建调度计划任务的灵活参数;定时schedule存计划执行的对应JSON',
  `type` varchar(10) DEFAULT NULL COMMENT '触发条件：手动触发manual、定时schedule、定时触发trigger',
  `exceptional` varchar(20) NOT NULL DEFAULT 'stop' COMMENT '报错如何处理：跳过jump、停止stop、重试后跳过retry_jump、重试后停止retry_stop',
  `retry_num` int(11) DEFAULT NULL COMMENT '只有exceptional为retry时，记录的重试次数',
  `timeout_enable` smallint(6) DEFAULT NULL COMMENT '是否启用超时时间 1:启用 0:不启用',
  `timeout` int(11) DEFAULT '9999' COMMENT '超时时间',
  `queue_enable` smallint(6) DEFAULT '0' COMMENT '是否启用排队 1:启用 0:不启用',
  `screen_record_enable` smallint(6) DEFAULT '0' COMMENT '是否开启录屏 1:启用 0:不启用',
  `virtual_desktop_enable` smallint(6) DEFAULT '0' COMMENT '是否开启虚拟桌面 1:启用 0:不启用',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(6) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`dispatch_task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1965712054394085377 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.dispatch_task_execute_record definition

CREATE TABLE `dispatch_task_execute_record` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `dispatch_task_id` bigint(20) DEFAULT NULL COMMENT '调度模式计划任务id',
  `dispatch_task_execute_id` bigint(20) DEFAULT NULL COMMENT '调度模式计划任务执行id',
  `count` int(11) DEFAULT NULL COMMENT '执行批次，1，2，3....',
  `dispatch_task_type` varchar(20) DEFAULT NULL COMMENT '触发条件：手动触发manual、定时schedule、定时触发trigger',
  `result` varchar(20) DEFAULT NULL COMMENT '执行结果枚举:成功success、失败error、执行中executing、中止cancel、下发失败dispatch_error、执行失败exe_error',
  `start_time` datetime DEFAULT NULL COMMENT '执行开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '执行结束时间',
  `execute_time` bigint(20) DEFAULT NULL COMMENT '执行耗时 单位秒',
  `terminal_id` char(36) DEFAULT NULL COMMENT '终端唯一标识，如设备mac地址',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `task_detail_json` mediumtext COMMENT '任务详情',
  `deleted` smallint(6) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`),
  KEY `idx_dispatch_task_teminal_task_id` (`dispatch_task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=113 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.dispatch_task_robot definition

CREATE TABLE `dispatch_task_robot` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `dispatch_task_id` bigint(20) DEFAULT NULL COMMENT '调度模式计划任务id',
  `robot_id` varchar(30) DEFAULT NULL COMMENT '机器人ID',
  `online` tinyint(3) DEFAULT NULL COMMENT '是否启用版本： 0:未启用,1:已启用',
  `version` int(11) DEFAULT NULL COMMENT '机器人版本',
  `param_json` mediumtext COMMENT '机器人配置参数',
  `sort` int(11) DEFAULT NULL COMMENT '排序, 越小越靠前',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(6) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`),
  KEY `idx_dispatch_task_teminal_task_id` (`dispatch_task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=86 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.dispatch_task_robot_execute_record definition

CREATE TABLE `dispatch_task_robot_execute_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `execute_id` bigint(20) DEFAULT NULL COMMENT '机器人执行id',
  `dispatch_task_execute_id` bigint(20) DEFAULT NULL COMMENT '调度模式计划任务执行id',
  `robot_id` varchar(100) DEFAULT NULL COMMENT '机器人id',
  `robot_version` int(11) DEFAULT NULL COMMENT '机器人版本号',
  `start_time` timestamp NULL DEFAULT NULL COMMENT '开始时间',
  `end_time` timestamp NULL DEFAULT NULL COMMENT '结束时间',
  `execute_time` bigint(20) DEFAULT NULL COMMENT '执行耗时 单位秒',
  `result` varchar(20) DEFAULT NULL COMMENT '执行结果枚举:：robotFail:失败， robotSuccess:成功，robotCancel:取消(中止)，robotExecute:正在执行',
  `param_json` mediumtext COMMENT '机器人执行参数',
  `error_reason` varchar(255) DEFAULT NULL COMMENT '错误原因',
  `execute_log` longtext COMMENT '日志内容',
  `video_local_path` varchar(200) DEFAULT NULL COMMENT '视频记录的本地存储路径',
  `dept_id_path` varchar(100) DEFAULT NULL COMMENT '部门全路径编码',
  `terminal_id` char(36) DEFAULT NULL COMMENT '终端唯一标识，如设备mac地址',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(6) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=85 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.dispatch_task_terminal definition

CREATE TABLE `dispatch_task_terminal` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `dispatch_task_id` bigint(20) DEFAULT NULL COMMENT '调度模式计划任务id',
  `terminal_or_group` varchar(10) DEFAULT NULL COMMENT '触发条件：终端teminal、终端分组group',
  `execute_method` varchar(10) DEFAULT NULL COMMENT '执行方式：随机一台random_one、全部执行all',
  `value` mediumtext COMMENT '具体值：存储 list<id> ; 其中终端对应：terminal_id（表terminal） 分组对应：id （terminal_group_name）',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(6) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`),
  KEY `idx_dispatch_task_teminal_task_id` (`dispatch_task_id`)
) ENGINE=InnoDB AUTO_INCREMENT=62 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.file definition

CREATE TABLE `file` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '主键ID',
  `file_id` varchar(50) DEFAULT NULL COMMENT '文件对应的uuid',
  `path` varchar(100) DEFAULT NULL COMMENT '文件在s3上对应的路径',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `deleted` int(11) DEFAULT 0 COMMENT '逻辑删除标志位',
  `file_name` varchar(1000) DEFAULT NULL COMMENT '文件真实名称',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=4406 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='文件表';


-- rpa.his_base definition

CREATE TABLE `his_base` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `dept_id_path` varchar(100) DEFAULT NULL COMMENT '部门全路径编码',
  `execute_success` bigint(20) DEFAULT NULL COMMENT '累计执行成功次数',
  `execute_fail` bigint(20) DEFAULT NULL COMMENT '累计执行失败次数',
  `execute_abort` bigint(20) DEFAULT NULL COMMENT '累计执行中止次数',
  `robot_num` bigint(20) DEFAULT NULL COMMENT '累计机器人总数',
  `execute_total` bigint(20) DEFAULT NULL COMMENT '机器人累计执行次数',
  `execute_time_total` bigint(20) DEFAULT NULL COMMENT '全部机器人或全部终端累计执行时长，单位秒，只计算成功的',
  `execute_success_rate` decimal(5,2) DEFAULT NULL COMMENT '累计执行成功率',
  `user_num` bigint(20) DEFAULT NULL COMMENT '累计用户数量',
  `count_time` timestamp NULL DEFAULT NULL COMMENT '统计时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) NOT NULL DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `terminal` bigint(20) DEFAULT NULL COMMENT '终端数量',
  `labor_save` bigint(20) DEFAULT NULL COMMENT '节省的人力',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=295 DEFAULT CHARSET=utf8 COMMENT='全部机器人和全部终端趋势表';


-- rpa.his_data_enum definition

CREATE TABLE `his_data_enum` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `parent_code` varchar(100) DEFAULT NULL,
  `icon` varchar(100) DEFAULT NULL,
  `field` varchar(100) DEFAULT NULL,
  `text` varchar(100) DEFAULT NULL,
  `num` varchar(100) DEFAULT NULL,
  `unit` varchar(100) DEFAULT NULL,
  `percent` varchar(100) DEFAULT NULL,
  `tip` varchar(100) DEFAULT NULL,
  `order` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8 COMMENT='监控管理数据概览卡片配置数据枚举';


-- rpa.his_robot definition

CREATE TABLE `his_robot` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `execute_num_total` bigint(20) DEFAULT NULL COMMENT '当日执行总次数',
  `execute_success` bigint(20) DEFAULT NULL COMMENT '每日成功次数',
  `execute_fail` bigint(20) DEFAULT NULL COMMENT '每日失败次数',
  `execute_abort` bigint(20) DEFAULT NULL COMMENT '每日中止次数',
  `execute_success_rate` decimal(5,2) DEFAULT NULL COMMENT '每日成功率',
  `execute_time` bigint(20) DEFAULT NULL COMMENT '每日执行时长，单位秒',
  `count_time` timestamp NULL DEFAULT NULL COMMENT '统计时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `robot_id` varchar(100) DEFAULT NULL,
  `user_id` char(36) DEFAULT NULL COMMENT '用户id',
  `dept_id_path` varchar(100) DEFAULT NULL COMMENT '部门全路径id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=147 DEFAULT CHARSET=utf8 COMMENT='单个机器人趋势表,当日数据';


-- rpa.his_terminal definition

CREATE TABLE `his_terminal` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `dept_id_path` varchar(36) DEFAULT NULL COMMENT '部门全路径id',
  `terminal_id` varchar(100) DEFAULT NULL COMMENT '设备mac',
  `execute_time` bigint(20) DEFAULT NULL COMMENT '每日执行时长',
  `execute_num` bigint(20) DEFAULT NULL COMMENT '终端每日执行次数',
  `count_time` timestamp NULL DEFAULT NULL COMMENT '统计时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`),
  KEY `his_terminal_terminal_id_IDX` (`terminal_id`) USING BTREE,
  KEY `his_terminal_tenant_id_IDX` (`tenant_id`,`dept_id_path`) USING BTREE,
  KEY `his_terminal_count_time_IDX` (`count_time`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=46 DEFAULT CHARSET=utf8 COMMENT='单个终端趋势表';


-- rpa.notify_send definition

CREATE TABLE `notify_send` (
  `tenant_id` varchar(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '接受者所在租户',
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` varchar(50) CHARACTER SET utf8 DEFAULT NULL COMMENT '接收者',
  `message_info` varchar(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '消息体id',
  `message_type` varchar(20) CHARACTER SET utf8 DEFAULT NULL COMMENT '消息类型：邀人消息teamMarketInvite，更新消息teamMarketUpdate',
  `operate_result` smallint(2) DEFAULT NULL COMMENT '操作结果：未读1， 已读2，已加入3，已拒绝4',
  `market_id` varchar(500) CHARACTER SET utf8 DEFAULT NULL COMMENT '市场id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(2) DEFAULT '0' COMMENT '删除标识',
  `user_type` varchar(10) CHARACTER SET utf8 DEFAULT NULL COMMENT '成员类型：owner,admin,consumer',
  `app_name` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=202 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='消息通知-消息表';


-- rpa.openapi_auth definition

CREATE TABLE `openapi_auth` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(50) DEFAULT NULL,
  `user_id` char(36) DEFAULT NULL COMMENT '用户id',
  `api_key` varchar(100) DEFAULT NULL,
  `prefix` varchar(10) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  `is_active` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `UNIQUE` (`api_key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='openapi鉴权储存';


-- rpa.openai_workflows definition

CREATE TABLE `openai_workflows` (
  `project_id` varchar(100) NOT NULL COMMENT '项目ID（主键）',
  `name` varchar(100) NOT NULL COMMENT '工作流名称',
  `description` varchar(500) DEFAULT NULL COMMENT '工作流描述',
  `version` int(11) NOT NULL DEFAULT '1' COMMENT '工作流版本号',
  `status` int(11) NOT NULL DEFAULT '1' COMMENT '工作流状态（1=激活，0=禁用）',
  `user_id` varchar(50) NOT NULL COMMENT '用户ID',
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `english_name` varchar(100) DEFAULT NULL COMMENT '翻译后的英文名称',
  `parameters` text COMMENT '存储JSON字符串格式的参数',
  PRIMARY KEY (`project_id`),
  KEY `idx_name` (`name`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- rpa.openai_executions definition

CREATE TABLE `openai_executions` (
  `id` varchar(36) NOT NULL COMMENT '执行记录ID（UUID）',
  `project_id` varchar(100) NOT NULL COMMENT '项目ID（关联工作流）',
  `status` varchar(20) NOT NULL DEFAULT 'PENDING' COMMENT '执行状态（PENDING/RUNNING/COMPLETED/FAILED/CANCELLED）',
  `parameters` text COMMENT '执行参数（JSON格式）',
  `result` text COMMENT '执行结果（JSON格式）',
  `error` text COMMENT '错误信息',
  `user_id` varchar(50) NOT NULL COMMENT '用户ID',
  `exec_position` varchar(50) NOT NULL DEFAULT 'EXECUTOR' COMMENT '执行位置',
  `version` int(11) DEFAULT NULL COMMENT '工作流版本号',
  `start_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '结束时间',
  PRIMARY KEY (`id`),
  KEY `idx_project_id` (`project_id`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_status` (`status`),
  KEY `idx_start_time` (`start_time`),
  CONSTRAINT `openai_executions_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `openai_workflows` (`project_id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- rpa.pypi_packages definition

CREATE TABLE `pypi_packages` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `package_name` varchar(255) NOT NULL,
  `oss_path` varchar(255) NOT NULL,
  `visibility` tinyint(1) DEFAULT '1' COMMENT 'visibility 1：公共可见包 2：个人私有包 3：灰度包，部分人可见',
  `user_id` char(36) DEFAULT '0' COMMENT '发布用户id',
  `create_time` datetime DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `unique_key` (`package_name`,`visibility`,`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- rpa.robot_design definition

CREATE TABLE `robot_design` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `robot_id` varchar(100) DEFAULT NULL COMMENT '机器人唯一id，获取的应用id',
  `name` varchar(100) DEFAULT NULL COMMENT '当前名字，用于列表展示',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  `app_id` varchar(50) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT 'appmarketResource中的应用id',
  `app_version` int(11) DEFAULT NULL COMMENT '获取的应用：应用市场版本',
  `market_id` varchar(20) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '获取的应用：市场id',
  `resource_status` varchar(20) DEFAULT NULL COMMENT '资源状态：toObtain, obtained, toUpdate',
  `data_source` varchar(20) DEFAULT NULL COMMENT '来源：create 自己创建 ； market 市场获取 ',
  `transform_status` varchar(20) DEFAULT NULL COMMENT 'editing 编辑中，published 已发版，shared 已上架，locked锁定（无法编辑）',
  `edit_enable` varchar(100) DEFAULT NULL COMMENT '废弃',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3481 DEFAULT CHARSET=utf8 COMMENT='云端机器人表';


-- rpa.robot_execute definition

CREATE TABLE `robot_execute` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `robot_id` varchar(100) DEFAULT NULL COMMENT '机器人唯一id，获取的应用id',
  `name` varchar(100) DEFAULT NULL COMMENT '当前名字，用于列表展示',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  `app_id` varchar(50) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT 'appmarketResource中的应用id',
  `app_version` int(11) DEFAULT NULL COMMENT '获取的应用：应用市场版本',
  `market_id` varchar(20) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '获取的应用：市场id',
  `resource_status` varchar(20) DEFAULT NULL COMMENT '资源状态：toObtain, obtained, toUpdate',
  `data_source` varchar(20) DEFAULT NULL COMMENT '来源：create 自己创建 ； market 市场获取 ；deploy卓越中心部署',
  `param_detail` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '运行前用户自定义的表单参数',
  `dept_id_path` varchar(200) DEFAULT NULL COMMENT '部门全路径',
  `type` varchar(10) DEFAULT NULL COMMENT '最新版本机器人的类型，web，other',
  `latest_release_time` timestamp NULL DEFAULT NULL COMMENT '最新版本发版时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2667 DEFAULT CHARSET=utf8 COMMENT='云端机器人表';


-- rpa.robot_execute_record definition

CREATE TABLE `robot_execute_record` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `execute_id` varchar(30) DEFAULT NULL COMMENT '执行id',
  `robot_id` varchar(100) DEFAULT NULL COMMENT '机器人id',
  `robot_version` int(10) DEFAULT NULL COMMENT '机器人版本号',
  `start_time` timestamp NULL DEFAULT NULL COMMENT '开始时间',
  `end_time` timestamp NULL DEFAULT NULL COMMENT '结束时间',
  `execute_time` bigint(20) DEFAULT NULL COMMENT '执行耗时 单位秒',
  `mode` varchar(60) DEFAULT NULL COMMENT '运行位置：工程列表页PROJECT_LIST ； 工程编辑页EDIT_PAGE； 计划任务CRONTAB ； 执行器运行 EXECUTOR',
  `task_execute_id` varchar(30) DEFAULT NULL COMMENT '计划任务执行id，即schedule_task_execute的execute_id',
  `result` varchar(20) DEFAULT NULL COMMENT '执行结果：robotFail:失败， robotSuccess:成功，robotCancel:取消(中止)，robotExecute:正在执行',
  `error_reason` varchar(255) DEFAULT NULL COMMENT '错误原因',
  `execute_log` longtext COMMENT '日志内容',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  `video_local_path` varchar(200) DEFAULT NULL COMMENT '视频记录的本地存储路径',
  `dept_id_path` varchar(100) DEFAULT NULL COMMENT '部门全路径编码',
  `terminal_id` char(36) CHARACTER SET utf8mb4 DEFAULT NULL COMMENT '终端唯一标识，如设备mac地址',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57946 DEFAULT CHARSET=utf8 COMMENT='云端机器人执行记录表';


-- rpa.robot_version definition

CREATE TABLE `robot_version` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id',
  `robot_id` varchar(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '机器人id',
  `version` int(10) DEFAULT NULL COMMENT '版本号',
  `introduction` longtext CHARACTER SET utf8 COMMENT '简介',
  `update_log` longtext CHARACTER SET utf8 COMMENT '更新日志',
  `use_description` longtext CHARACTER SET utf8 COMMENT '使用说明',
  `online` smallint(2) DEFAULT '0' COMMENT '是否启用 0:未启用,1:已启用',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL,
  `param` text CHARACTER SET utf8,
  `param_detail` text CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci COMMENT '发版时拖的表单参数信息',
  `video_id` varchar(100) DEFAULT NULL COMMENT '视频地址id',
  `appendix_id` varchar(100) DEFAULT NULL COMMENT '附件地址id',
  `icon` varchar(100) DEFAULT NULL COMMENT '图标',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2083 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='云端机器人版本表';


-- rpa.schedule_task definition

CREATE TABLE `schedule_task` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `task_id` varchar(100) DEFAULT NULL COMMENT '计划任务id',
  `name` varchar(64) DEFAULT NULL COMMENT '任务名称',
  `description` varchar(255) DEFAULT NULL COMMENT '描述',
  `exception_handle_way` varchar(64) DEFAULT NULL COMMENT '异常处理方式：stop停止  skip跳过',
  `run_mode` varchar(64) DEFAULT NULL COMMENT '执行模式，循环cycle, 定时fixed,自定义custom',
  `cycle_frequency` varchar(10) DEFAULT NULL COMMENT '循环频率,单位秒，-1为只有一次，3600，，，custom',
  `cycle_num` varchar(64) DEFAULT NULL COMMENT '自定义循环，循环类型，每1小时，每3小时，，自定义',
  `cycle_unit` varchar(20) DEFAULT NULL COMMENT '自定义循环，循环单位：minutes, hour',
  `status` varchar(64) DEFAULT NULL COMMENT '状态：doing执行中 close已结束 ready待执行',
  `enable` tinyint(1) DEFAULT NULL COMMENT '启/禁用',
  `schedule_type` varchar(64) DEFAULT NULL COMMENT '定时方式,day,month,week',
  `schedule_rule` varchar(255) DEFAULT NULL COMMENT '定时配置（配置对象）',
  `start_at` datetime DEFAULT NULL COMMENT '开始时间',
  `end_at` datetime DEFAULT NULL COMMENT '结束时间',
  `tenant_id` char(36) DEFAULT NULL,
  `enable_queue_execution` tinyint(1) DEFAULT NULL COMMENT '是否排队执行',
  `cron_expression` varchar(50) DEFAULT NULL COMMENT 'cron表达式',
  `last_time` timestamp NULL DEFAULT NULL COMMENT '上次拉取时的nextTime',
  `next_time` timestamp NULL DEFAULT NULL COMMENT '下次执行时间',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建人ID',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(6) DEFAULT NULL,
  `pull_time` timestamp NULL DEFAULT NULL COMMENT '上次拉取时间',
  `log_enable` varchar(5) CHARACTER SET utf8mb4 DEFAULT 'F' COMMENT '是否开启日志记录',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='调度任务';


-- rpa.schedule_task_execute definition

CREATE TABLE `schedule_task_execute` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `task_id` varchar(20) DEFAULT NULL COMMENT '任务ID',
  `task_execute_id` varchar(20) DEFAULT NULL COMMENT '计划任务执行id',
  `count` int(11) DEFAULT NULL COMMENT '执行批次，1，2，3....',
  `result` varchar(20) DEFAULT NULL COMMENT '任务状态枚举    成功  "success"     # 启动失败     "start_error"     # 执行失败      "exe_error"     # 取消     CANCEL = "cancel"     # 执行中   "executing"',
  `start_time` datetime DEFAULT NULL COMMENT '执行开始时间',
  `end_time` datetime DEFAULT NULL COMMENT '执行结束时间',
  `tenant_id` char(36) DEFAULT NULL,
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=894952 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='计划任务执行记录';


-- rpa.schedule_task_pull_log definition

CREATE TABLE `schedule_task_pull_log` (
  `id` bigint(20) DEFAULT NULL,
  `task_id` varchar(100) CHARACTER SET utf8 DEFAULT NULL COMMENT '计划任务id',
  `pull_time` timestamp NULL DEFAULT NULL COMMENT '上次拉取时间',
  `last_time` timestamp NULL DEFAULT NULL COMMENT '上次拉取时的nextTime',
  `next_time` timestamp NULL DEFAULT NULL COMMENT '下次执行时间',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建人ID',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.schedule_task_robot definition

CREATE TABLE `schedule_task_robot` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `task_id` varchar(30) DEFAULT NULL COMMENT '任务ID',
  `robot_id` varchar(30) DEFAULT NULL COMMENT '机器人ID',
  `sort` int(11) DEFAULT NULL COMMENT '排序, 越小越靠前',
  `tenant_id` char(36) DEFAULT NULL,
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `param_json` mediumtext COMMENT '计划任务相关参数',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=1070 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='计划任务机器人列表';


-- rpa.shared_file definition

CREATE TABLE `shared_file` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `file_id` bigint(20) DEFAULT NULL COMMENT '文件对应的uuid',
  `path` varchar(500) DEFAULT NULL COMMENT '文件在s3上对应的路径',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `file_name` varchar(1000) DEFAULT NULL COMMENT '文件真实名称',
  `tags` varchar(512) DEFAULT NULL COMMENT '文件标签名称集合',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者ID',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `file_type` tinyint(4) DEFAULT NULL COMMENT '文件类型: 0-位置类型 1-文本 2-WORD 3-PDF',
  `file_index_status` tinyint(4) DEFAULT NULL COMMENT '文件向量化状态:1-初始化 2-完成 3-失败',
  `dept_id` varchar(100) DEFAULT NULL COMMENT '部门id',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='共享文件表';


-- rpa.shared_file_tag definition

CREATE TABLE `shared_file_tag` (
  `tag_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '标签id',
  `tag_name` varchar(255) DEFAULT NULL COMMENT '标签真实名称',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者ID',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者ID',
  PRIMARY KEY (`tag_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1963072518379114497 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='共享文件标签表';


-- rpa.shared_sub_var definition

CREATE TABLE `shared_sub_var` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT COMMENT '子变量id',
  `shared_var_id` bigint(20) unsigned NOT NULL COMMENT '共享变量id',
  `var_name` varchar(255) DEFAULT NULL COMMENT '子变量名',
  `var_type` varchar(20) DEFAULT NULL COMMENT '变量类型：text/password/array',
  `var_value` varchar(750) DEFAULT NULL COMMENT '变量具体值，加密则为密文，否则为明文',
  `encrypt` tinyint(1) DEFAULT NULL COMMENT '是否加密:1-加密',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_shared_var_id` (`shared_var_id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='共享变量-子变量';


-- rpa.shared_var definition

CREATE TABLE `shared_var` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `shared_var_name` varchar(255) DEFAULT NULL COMMENT '共享变量名',
  `status` tinyint(1) DEFAULT NULL COMMENT '启用状态：1启用',
  `remark` varchar(255) DEFAULT NULL COMMENT '变量说明',
  `dept_id` char(36) DEFAULT NULL COMMENT '所屬部门ID',
  `usage_type` varchar(10) DEFAULT NULL COMMENT '可使用账号类别(all/dept/select)：所有人：all、所属部门所有人：dept、指定人：select',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `shared_var_type` varchar(20) DEFAULT NULL COMMENT '共享变量类型：text/password/array/group',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_dept_id_path` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='共享变量信息';


-- rpa.shared_var_key_tenant definition

CREATE TABLE `shared_var_key_tenant` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `tenant_id` varchar(36) NOT NULL,
  `key` varchar(500) DEFAULT NULL COMMENT '共享变量租户密钥',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_tenant_id` (`tenant_id`)
) ENGINE=InnoDB AUTO_INCREMENT=1967981807948963842 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='共享变量租户密钥表';


-- rpa.shared_var_user definition

CREATE TABLE `shared_var_user` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `shared_var_id` bigint(20) unsigned NOT NULL COMMENT '共享变量id',
  `user_id` char(36) DEFAULT NULL COMMENT '用户id',
  `user_name` varchar(100) DEFAULT NULL COMMENT '用户姓名',
  `user_phone` varchar(100) DEFAULT NULL COMMENT '用户手机号',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_shared_var_id` (`shared_var_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='共享变量与用户的映射表；N:N映射';


-- rpa.sms_record definition

CREATE TABLE `sms_record` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'ID',
  `receiver` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '短信接收者',
  `send_type` varchar(30) CHARACTER SET utf8 DEFAULT NULL COMMENT '短信类型',
  `send_result` varchar(20) CHARACTER SET utf8 DEFAULT NULL COMMENT '发送结果',
  `fail_reason` varchar(3000) CHARACTER SET utf8 DEFAULT NULL COMMENT '失败原因',
  `create_by` int(11) DEFAULT NULL COMMENT '创建者',
  `create_time` datetime DEFAULT NULL COMMENT '创建时间',
  `update_by` int(11) DEFAULT NULL COMMENT '更新者',
  `update_time` datetime DEFAULT NULL COMMENT '更新时间',
  `deleted` int(11) DEFAULT NULL COMMENT '是否已删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.task_mail definition

CREATE TABLE `task_mail` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_id` char(36) DEFAULT NULL,
  `tenant_id` char(36) DEFAULT NULL,
  `resource_id` varchar(255) DEFAULT NULL,
  `email_service` varchar(50) DEFAULT NULL COMMENT '邮箱服务器，163Email、126Email、qqEmail、customEmail',
  `email_protocol` varchar(50) DEFAULT NULL COMMENT '使用协议，POP3,IMAP',
  `email_service_address` varchar(255) DEFAULT NULL COMMENT '邮箱服务器地址',
  `port` varchar(50) DEFAULT NULL COMMENT '邮箱服务器端口',
  `enable_ssl` tinyint(1) DEFAULT NULL COMMENT '是否使用SSL',
  `email_account` varchar(255) DEFAULT NULL COMMENT '邮箱账号',
  `authorization_code` varchar(255) DEFAULT NULL COMMENT '邮箱授权码',
  `deleted` tinyint(1) DEFAULT '0' COMMENT '是否删除',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=40 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- rpa.terminal definition

CREATE TABLE `terminal` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT '主键id，用于数据定时统计的进度管理',
  `terminal_id` char(36) NOT NULL COMMENT '终端唯一标识，如设备mac地址',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `dept_id` varchar(100) DEFAULT NULL COMMENT '部门id',
  `dept_id_path` varchar(100) DEFAULT NULL COMMENT '部门全路径id',
  `name` varchar(200) DEFAULT NULL COMMENT '终端名称',
  `account` varchar(100) DEFAULT NULL COMMENT '设备账号',
  `os` varchar(50) DEFAULT NULL COMMENT '操作系统',
  `ip` varchar(200) DEFAULT NULL COMMENT 'ip列表',
  `actual_client_ip` varchar(100) DEFAULT NULL COMMENT '实际连接源IP，服务端检测后的推荐ip',
  `custom_ip` varchar(20) DEFAULT NULL COMMENT '用户自定义ip',
  `port` int(11) DEFAULT NULL COMMENT '端口',
  `status` varchar(20) DEFAULT NULL COMMENT '当前状态，运行中busy，空闲free，离线offline，单机中standalone',
  `remark` varchar(100) DEFAULT NULL COMMENT '终端描述',
  `user_id` varchar(100) DEFAULT NULL COMMENT '最后登录的用户的id，用于根据姓名筛选',
  `os_name` char(36) DEFAULT NULL COMMENT '信息维护：电脑设备用户名',
  `os_pwd` varchar(200) DEFAULT NULL COMMENT '信息维护：电脑设备用户密码',
  `is_dispatch` smallint(6) DEFAULT NULL COMMENT '是否调度模式',
  `monitor_url` varchar(100) DEFAULT NULL COMMENT '视频监控url',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '终端记录创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) NOT NULL DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `custom_port` int(11) DEFAULT NULL COMMENT '自定义端口',
  PRIMARY KEY (`id`),
  KEY `cloud_terminal_mac_tenant_index` (`tenant_id`),
  KEY `cloud_terminal_tenant_id_IDX` (`tenant_id`,`dept_id_path`),
  KEY `cloud_terminal_user_id_IDX` (`os_name`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='终端表';


-- rpa.terminal_group definition

CREATE TABLE `terminal_group` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `group_id` bigint(20) DEFAULT NULL COMMENT '分组名',
  `terminal_id` bigint(20) DEFAULT NULL COMMENT '终端id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_group_id` (`group_id`),
  KEY `idx_terminal_id` (`terminal_id`)
) ENGINE=InnoDB AUTO_INCREMENT=95 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='终端分组-分组与终端的映射表；N:N映射';


-- rpa.terminal_group_info definition

CREATE TABLE `terminal_group_info` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `group_name` varchar(100) DEFAULT NULL COMMENT '分组名',
  `terminal_id` varchar(20) DEFAULT NULL COMMENT '终端id',
  `dept_id` char(36) DEFAULT NULL COMMENT '所屬部门ID',
  `usage_type` varchar(10) DEFAULT NULL COMMENT '可使用账号类别(all/dept/select)：所有人：all、所属部门所有人：dept、指定人：select',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_terminal_id` (`terminal_id`),
  KEY `idx_dept_id_path` (`dept_id`)
) ENGINE=InnoDB AUTO_INCREMENT=49 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='终端分组';


-- rpa.terminal_group_user definition

CREATE TABLE `terminal_group_user` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `group_id` varchar(20) DEFAULT NULL COMMENT '分组名',
  `user_id` char(36) DEFAULT NULL COMMENT '用户id',
  `creator_id` char(36) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` char(36) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  `user_name` varchar(100) DEFAULT NULL COMMENT '用户姓名',
  `user_phone` varchar(100) DEFAULT NULL COMMENT '用户手机号',
  PRIMARY KEY (`id`) USING BTREE,
  KEY `idx_group_id` (`group_id`),
  KEY `idx_user_id` (`user_id`)
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='终端分组-分组与用户的映射表；N:N映射';


-- rpa.terminal_login_history definition

CREATE TABLE `terminal_login_history` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `terminal_id` varchar(20) DEFAULT NULL COMMENT '终端id',
  `account` varchar(100) DEFAULT NULL COMMENT '账号',
  `user_name` varchar(100) DEFAULT NULL COMMENT '用户名',
  `login_time` timestamp NULL DEFAULT NULL COMMENT '登录时间',
  `logout_time` timestamp NULL DEFAULT NULL COMMENT '登出时间',
  `creator_id` bigint(20) DEFAULT NULL COMMENT '创建者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updater_id` bigint(20) DEFAULT NULL COMMENT '更新者id',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC COMMENT='终端登录账号历史记录';


-- rpa.terminal_login_record definition

CREATE TABLE `terminal_login_record` (
  `id` char(36) COLLATE utf8mb4_bin NOT NULL,
  `login_time` timestamp NULL DEFAULT NULL COMMENT '登录时间',
  `logout_time` timestamp NULL DEFAULT NULL COMMENT '登出时间',
  `terminal_id` varchar(20) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '终端id',
  `dept_id` char(36) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '部门id',
  `dept_id_path` varchar(100) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '部门全路径id',
  `ip` varchar(255) COLLATE utf8mb4_bin DEFAULT NULL,
  `login_status` int(11) NOT NULL COMMENT '是否登录成功{0:登录失败，1:登录成功}',
  `remark` varchar(1000) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '操作描述',
  `creator_id` char(36) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '创建者id',
  `updater_id` char(36) COLLATE utf8mb4_bin DEFAULT NULL COMMENT '更新者id',
  `create_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `deleted` smallint(1) DEFAULT '0' COMMENT '是否删除 0：未删除，1：已删除',
  PRIMARY KEY (`id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COLLATE=utf8mb4_bin COMMENT='终端登录账号历史记录';


-- rpa.trigger_task definition

CREATE TABLE `trigger_task` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `task_id` bigint(20) DEFAULT NULL COMMENT '触发器计划任务id',
  `name` varchar(50) DEFAULT NULL COMMENT '触发器计划任务名称',
  `task_json` mediumtext COMMENT '构建计划任务的灵活参数',
  `creator_id` char(36) DEFAULT NULL,
  `updater_id` char(36) DEFAULT NULL,
  `deleted` smallint(1) NOT NULL DEFAULT '0',
  `create_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '更新时间',
  `task_type` varchar(20) DEFAULT NULL COMMENT '任务类型：定时schedule、邮件mail、文件file、热键hotKey:',
  `enable` smallint(1) NOT NULL DEFAULT '0' COMMENT '是否启用',
  `exceptional` varchar(20) NOT NULL DEFAULT 'stop' COMMENT '报错如何处理：跳过jump、停止stop',
  `timeout` int(10) DEFAULT '9999' COMMENT '超时时间',
  `tenant_id` char(36) DEFAULT NULL COMMENT '租户id',
  `queue_enable` smallint(6) DEFAULT '0' COMMENT '是否启用排队 1:启用 0:不启用',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=194 DEFAULT CHARSET=utf8 COMMENT='触发器计划任务';