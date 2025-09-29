package com.iflytek.astron.console.hub.strategy.publish.impl;

import com.iflytek.astron.console.commons.enums.bot.BotPublishTypeEnum;
import com.iflytek.astron.console.commons.response.ApiResult;
import com.iflytek.astron.console.hub.dto.publish.mcp.McpPublishRequestDto;
import com.iflytek.astron.console.hub.service.publish.McpService;
import com.iflytek.astron.console.hub.strategy.publish.PublishStrategy;
import com.alibaba.fastjson2.JSON;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

/**
 * MCP publish strategy implementation
 * Handles bot publishing to MCP server channel
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class McpPublishStrategy implements PublishStrategy {

    private final McpService mcpService;

    @Override
    public ApiResult<String> publish(Integer botId, Object publishData, String currentUid, Long spaceId) {
        log.info("Publishing bot to MCP: botId={}, currentUid={}, spaceId={}", botId, currentUid, spaceId);
        
        try {
            // Parse MCP publish data
            McpPublishRequestDto mcpRequest = parsePublishData(publishData, botId);
            
            log.debug("MCP publish request: {}", JSON.toJSONString(mcpRequest));
            
            // Delegate to existing MCP publish logic
            mcpService.publishMcp(mcpRequest, currentUid, spaceId);
            
            log.info("MCP publish completed successfully: botId={}, serverName={}", 
                    botId, mcpRequest.getServerName());
            return ApiResult.success("Bot published as MCP server successfully");
            
        } catch (Exception e) {
            log.error("MCP publish failed: botId={}, error={}", botId, e.getMessage(), e);
            throw e; // Let the controller handle the exception and convert to ApiResult
        }
    }

    @Override
    public ApiResult<String> offline(Integer botId, Object publishData, String currentUid, Long spaceId) {
        log.info("Offlining bot from MCP: botId={}, currentUid={}, spaceId={}", botId, currentUid, spaceId);
        
        try {
            // TODO: Implement MCP offline logic
            // Current McpService doesn't have offline method, need to add it
            // For now, just log the action
            log.warn("MCP offline not fully implemented yet: botId={}", botId);
            return ApiResult.success("MCP offline request processed (implementation pending)");
            
        } catch (Exception e) {
            log.error("MCP offline failed: botId={}, error={}", botId, e.getMessage(), e);
            throw e;
        }
    }

    @Override
    public String getPublishType() {
        return BotPublishTypeEnum.MCP.getCode();
    }

    /**
     * Parse publish data to McpPublishRequestDto
     */
    private McpPublishRequestDto parsePublishData(Object publishData, Integer botId) {
        if (publishData == null) {
            throw new IllegalArgumentException("MCP publish data cannot be null");
        }

        try {
            // Convert publishData to McpPublishRequestDto
            McpPublishRequestDto mcpRequest;
            
            if (publishData instanceof McpPublishRequestDto) {
                mcpRequest = (McpPublishRequestDto) publishData;
            } else {
                // Try to parse from JSON
                String jsonData = JSON.toJSONString(publishData);
                mcpRequest = JSON.parseObject(jsonData, McpPublishRequestDto.class);
            }
            
            // Ensure botId is set
            if (mcpRequest.getBotId() == null) {
                mcpRequest.setBotId(botId);
            }
            
            // Validate required fields
            if (mcpRequest.getServerName() == null || mcpRequest.getServerName().trim().isEmpty()) {
                throw new IllegalArgumentException("MCP server name is required");
            }
            
            return mcpRequest;
            
        } catch (Exception e) {
            log.error("Failed to parse MCP publish data: botId={}, data={}", botId, publishData, e);
            throw new IllegalArgumentException("Invalid MCP publish data format", e);
        }
    }
}
