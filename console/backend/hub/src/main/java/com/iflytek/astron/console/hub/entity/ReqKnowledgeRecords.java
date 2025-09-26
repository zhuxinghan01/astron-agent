package com.iflytek.astron.console.hub.entity;

import com.baomidou.mybatisplus.annotation.IdType;
import com.baomidou.mybatisplus.annotation.TableId;
import com.baomidou.mybatisplus.annotation.TableName;
import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;

import lombok.Builder;
import lombok.Data;

@Data
@TableName("req_knowledge_records")
@Schema(name = "ReqKnowledgeRecords", description = "知识检索结果记录表")
@Builder
public class ReqKnowledgeRecords {

    @TableId(type = IdType.AUTO)
    private Long id;

    @Schema(description = "用户ID")
    private String uid;

    @Schema(description = "用户提问的主键, 对应用户提问表的主键id")
    private Long reqId;

    @Schema(description = "用户提问的内容")
    private String reqMessage;

    @Schema(description = "检索出的知识")
    private String knowledge;

    @Schema(description = "创建时间")
    private LocalDateTime createTime;

    @Schema(description = "更新时间")
    private LocalDateTime updateTime;

    @Schema(description = "聊天窗口id, chat_list主键")
    private Long chatId;
}
