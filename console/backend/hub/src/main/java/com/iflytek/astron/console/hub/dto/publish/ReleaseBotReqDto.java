package com.iflytek.astron.console.hub.dto.publish;

import lombok.Data;

/**
 * @author yun-zhi-ztl
 */
@Data
public class ReleaseBotReqDto {
    private String botId;
    private String flowId;
    /**
     * Publishing channel
     */
    private Integer publishChannel;
    /**
     * Success/Failure/Under review
     */
    private String publishResult;

    private String description;
    /**
     * Version name/Version number
     */
    private String name;
}
