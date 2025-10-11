package com.iflytek.astron.console.hub.strategy.publish.impl;

import com.iflytek.astron.console.commons.enums.bot.ReleaseTypeEnum;
import com.iflytek.astron.console.commons.enums.PublishChannelEnum;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.response.ApiResult;
import com.iflytek.astron.console.commons.entity.model.McpData;
import com.iflytek.astron.console.commons.entity.bot.UserLangChainInfo;
import com.iflytek.astron.console.commons.mapper.bot.ChatBotBaseMapper;
import com.iflytek.astron.console.commons.mapper.model.McpDataMapper;
import com.iflytek.astron.console.commons.mapper.UserLangChainInfoMapper;
import com.iflytek.astron.console.hub.dto.publish.mcp.McpPublishRequestDto;
import com.iflytek.astron.console.hub.service.publish.BotPublishService;
import com.iflytek.astron.console.hub.service.workflow.WorkflowReleaseService;
import com.iflytek.astron.console.hub.dto.workflow.WorkflowReleaseResponseDto;
import com.iflytek.astron.console.commons.util.MaasUtil;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.context.request.RequestContextHolder;
import org.springframework.web.context.request.ServletRequestAttributes;
import com.iflytek.astron.console.hub.strategy.publish.PublishStrategy;
import com.alibaba.fastjson2.JSON;
import com.alibaba.fastjson2.JSONObject;

import jakarta.servlet.http.Cookie;
import jakarta.servlet.http.HttpServletRequest;
import java.time.LocalDateTime;
import java.util.Arrays;
import java.util.stream.Collectors;

/**
 * MCP publish strategy implementation Handles bot publishing to MCP server channel Based on
 * original MCPController#publishMCP logic
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class McpPublishStrategy implements PublishStrategy {

    private final ChatBotBaseMapper chatBotBaseMapper;
    private final UserLangChainInfoMapper userLangChainInfoMapper;
    private final McpDataMapper mcpDataMapper;
    private final BotPublishService botPublishService;
    private final WorkflowReleaseService workflowReleaseService;

    @Override
    @Transactional(rollbackFor = Exception.class)
    public ApiResult<Object> publish(Integer botId, Object publishData, String currentUid, Long spaceId) {
        log.info("Publishing bot to MCP: botId={}, currentUid={}, spaceId={}", botId, currentUid, spaceId);

        try {
            // Parse MCP publish data
            McpPublishRequestDto mcpRequest = parsePublishData(publishData, botId);
            log.debug("MCP publish request: {}", JSON.toJSONString(mcpRequest));

            // 1. Permission check (corresponds to botPermissionUtil.checkBot)
            int hasPermission = chatBotBaseMapper.checkBotPermission(botId, currentUid, spaceId);
            if (hasPermission == 0) {
                throw new BusinessException(ResponseEnum.BOT_NOT_EXISTS);
            }

            // 2. Check if workflow protocol exists (corresponds to userLangChainInfoDao.findListByBotId)
            UserLangChainInfo chainInfo = userLangChainInfoMapper.selectOne(
                    new com.baomidou.mybatisplus.core.conditions.query.QueryWrapper<UserLangChainInfo>()
                            .eq("bot_id", botId)
                            .orderByDesc("create_time")
                            .last("LIMIT 1"));
            if (chainInfo == null) {
                log.info("Bot workflow protocol not found: uid={}, botId={}", currentUid, botId);
                throw new BusinessException(ResponseEnum.BOT_CHAIN_SUBMIT_ERROR);
            }


            // 4. Use WorkflowReleaseService to handle version management and publishing
            // This replaces the separate getVersionName and recordMcpRelease calls
            WorkflowReleaseResponseDto publishResult = workflowReleaseService.publishWorkflow(botId, currentUid, spaceId, ReleaseTypeEnum.MCP.name());
            
            if (!publishResult.getSuccess()) {
                throw new BusinessException(ResponseEnum.SYSTEM_ERROR, 
                    "Failed to publish workflow for MCP: " + publishResult.getErrorMessage());
            }
            
            String versionName = publishResult.getWorkflowVersionName();
            log.info("Workflow published for MCP: botId={}, versionName={}", botId, versionName);

            // 5. Get cookies (corresponds to MassUtil.getRequestCookies(request))
            // Use RequestContextHolder to get current request context
            String cookie = getCurrentRequestCookies();

            // 6. Register MCP (corresponds to massUtil.registerMcp)
            JSONObject mcpResult = MaasUtil.registerMcp(cookie, chainInfo, mcpRequest, versionName);
            log.info("MCP registration result: {}", mcpResult);

            // 7. Save MCP data (corresponds to mcpDataDao.insert(mcp) in original project)
            mcpResult.put("createTime", LocalDateTime.now());
            mcpResult.put("uid", currentUid);
            mcpResult.put("spaceId", spaceId);
            mcpResult.put("botId", botId);
            mcpResult.put("versionName", versionName);
            mcpResult.put("released", 1);
            mcpResult.put("isDelete", 0);

            // Insert MCP data using the JSONObject result (similar to original project)
            int insertResult = insertMcpData(mcpResult);
            if (insertResult == 0) {
                throw new BusinessException(ResponseEnum.SYSTEM_ERROR);
            }

            // 8. Update publish channel
            botPublishService.updatePublishChannel(botId, currentUid, spaceId, PublishChannelEnum.MCP, true);

            log.info("MCP publish completed successfully: botId={}, versionName={}",
                    botId, versionName);

            return ApiResult.success(null); // No specific data needed for MCP publish

        } catch (Exception e) {
            log.error("MCP publish failed: botId={}, error={}", botId, e.getMessage(), e);
            throw e; // Let the controller handle the exception and convert to ApiResult
        }
    }

    @Override
    public ApiResult<Object> offline(Integer botId, Object publishData, String currentUid, Long spaceId) {
        log.info("Offlining bot from MCP: botId={}, currentUid={}, spaceId={}", botId, currentUid, spaceId);

        try {
            // TODO: Implement MCP offline logic
            // This would involve removing MCP server registration and updating database
            log.warn("MCP offline not fully implemented yet: botId={}", botId);

            // Update publish channel to remove MCP
            botPublishService.updatePublishChannel(botId, currentUid, spaceId, PublishChannelEnum.MCP, false);

            return ApiResult.success(null); // No specific data needed for MCP offline

        } catch (Exception e) {
            log.error("MCP offline failed: botId={}, error={}", botId, e.getMessage(), e);
            throw e;
        }
    }

    @Override
    public String getPublishType() {
        return ReleaseTypeEnum.MCP.name();
    }

    /**
     * Insert MCP data to database Corresponds to mcpDataDao.insert(mcp) in original project
     */
    private int insertMcpData(JSONObject mcpResult) {
        try {
            // Convert JSONObject to McpData entity for database insertion
            McpData mcpData = McpData.builder()
                    .botId(mcpResult.getInteger("botId"))
                    .uid(mcpResult.getString("uid"))
                    .spaceId(mcpResult.getLong("spaceId"))
                    .serverName(mcpResult.getString("serverName"))
                    .description(mcpResult.getString("description"))
                    .content(mcpResult.getString("content"))
                    .icon(mcpResult.getString("icon"))
                    .serverUrl(mcpResult.getString("serverUrl"))
                    .args(mcpResult.getString("args"))
                    .versionName(mcpResult.getString("versionName"))
                    .released(mcpResult.getInteger("released"))
                    .isDelete(mcpResult.getInteger("isDelete"))
                    .createTime(mcpResult.getObject("createTime", LocalDateTime.class))
                    .updateTime(LocalDateTime.now())
                    .build();

            log.info("Inserting MCP data: botId={}, serverName={}, versionName={}",
                    mcpData.getBotId(), mcpData.getServerName(), mcpData.getVersionName());

            return mcpDataMapper.insert(mcpData);

        } catch (Exception e) {
            log.error("Failed to insert MCP data: {}", mcpResult, e);
            throw new BusinessException(ResponseEnum.SYSTEM_ERROR, "Failed to save MCP data");
        }
    }

    /**
     * Get cookies from current HTTP request context This is a better practice than passing
     * HttpServletRequest directly to strategy
     */
    private String getCurrentRequestCookies() {
        try {
            ServletRequestAttributes attributes = (ServletRequestAttributes) RequestContextHolder.getRequestAttributes();
            if (attributes == null) {
                log.warn("No request context available, using empty cookies");
                return "";
            }
            
            HttpServletRequest request = attributes.getRequest();
            Cookie[] cookies = request.getCookies();
            
            if (cookies == null || cookies.length == 0) {
                return "";
            }
            
            return Arrays.stream(cookies)
                    .map(cookie -> cookie.getName() + "=" + cookie.getValue())
                    .collect(Collectors.joining("; "));
                    
        } catch (Exception e) {
            log.error("Failed to get request cookies", e);
            return "";
        }
    }

    /**
     * Parse publish data to McpPublishRequestDto
     */
    private McpPublishRequestDto parsePublishData(Object publishData, Integer botId) {
        if (publishData == null) {
            throw new IllegalArgumentException("MCP publish data cannot be null");
        }

        try {
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
