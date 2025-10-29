package com.iflytek.astron.console.commons.dto.workflow;

import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * Workflow information response DTO
 *
 * @author yingpeng
 */
@Data
@NoArgsConstructor
public class WorkflowInfoDto {

    /**
     * Plugin tools
     */
    private String openedTool;

    /**
     * Tool configuration list
     */
    private List<String> config;

    /**
     * Advanced configuration
     */
    private String advancedConfig;
}
