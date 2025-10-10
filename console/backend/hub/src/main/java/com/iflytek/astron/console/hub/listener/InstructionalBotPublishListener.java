package com.iflytek.astron.console.hub.listener;

import com.iflytek.astron.console.hub.event.BotPublishStatusChangedEvent;
import com.iflytek.astron.console.commons.entity.bot.ChatBotBase;
import com.iflytek.astron.console.commons.entity.bot.ChatBotMarket;
import com.iflytek.astron.console.commons.mapper.bot.ChatBotBaseMapper;
import com.iflytek.astron.console.commons.mapper.bot.ChatBotMarketMapper;
import com.iflytek.astron.console.commons.enums.ShelfStatusEnum;
import com.iflytek.astron.console.commons.exception.BusinessException;
import com.iflytek.astron.console.commons.constant.ResponseEnum;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

/**
 * Instructional Bot Publishing Event Listener
 *
 * Handles instructional bot specific publishing logic including:
 * - Market data synchronization
 * - Database updates
 * - Status management
 *
 * @author Omuigix
 */
@Slf4j
@Component
@RequiredArgsConstructor
public class InstructionalBotPublishListener {

    private final ChatBotBaseMapper chatBotBaseMapper;
    private final ChatBotMarketMapper chatBotMarketMapper;

    /**
     * Handle instructional bot publish status changed event
     * Processes market data synchronization and database updates
     */
    @EventListener
    @Transactional(rollbackFor = Exception.class)
    public void handleInstructionalBotPublishStatusChanged(BotPublishStatusChangedEvent event) {
        log.info("Handle instructional bot publish status change: botId={}, action={}, {} -> {}",
                event.getBotId(), event.getAction(), event.getOldStatus(), event.getNewStatus());

        try {
            Integer botId = event.getBotId();
            String uid = event.getUid();
            Long spaceId = event.getSpaceId();
            String action = event.getAction();
            Integer newStatus = event.getNewStatus();
            String newChannels = event.getPublishChannels();

            // 1. Validate bot permission
            int hasPermission = chatBotBaseMapper.checkBotPermission(botId, uid, spaceId);
            if (hasPermission == 0) {
                log.warn("Bot permission validation failed: botId={}, uid={}, spaceId={}", botId, uid, spaceId);
                return;
            }

            // 2. Handle database operations based on action type
            if (ShelfStatusEnum.isPublishAction(action)) {
                handleBotPublish(botId, uid, spaceId, newStatus, newChannels, event.isFirstPublish());
            } else if (ShelfStatusEnum.isOfflineAction(action)) {
                handleBotOffline(botId, uid, spaceId, newStatus, newChannels);
            }

            // 3. Log completion
            if (event.isFirstPublish()) {
                log.info("Instructional bot first publish completed: botId={}, uid={}, channels={}",
                        botId, uid, newChannels);
            } else if (event.isOnline()) {
                log.info("Instructional bot republished: botId={}, uid={}", botId, uid);
            } else if (event.isOffline()) {
                log.info("Instructional bot taken offline: botId={}, uid={}", botId, uid);
            }

        } catch (Exception e) {
            log.error("Instructional bot publish status change processing failed: botId={}", 
                    event.getBotId(), e);
            throw e; // Re-throw to trigger transaction rollback
        }
    }

    /**
     * Handle bot publish operation
     */
    private void handleBotPublish(Integer botId, String uid, Long spaceId, Integer newStatus, 
                                 String newChannels, boolean isFirstPublish) {
        if (isFirstPublish) {
            // First time publishing - insert new market record
            insertChatBotMarketRecord(botId, uid, spaceId, newStatus, newChannels);
        } else {
            // Re-publishing - sync all data from chat_bot_base to chat_bot_market
            syncBotDataToMarket(botId, uid, spaceId, newStatus, newChannels);
        }
    }

    /**
     * Handle bot offline operation
     */
    private void handleBotOffline(Integer botId, String uid, Long spaceId, Integer newStatus, String newChannels) {
        // Only update status and channels for offline operation
        int updateCount = chatBotMarketMapper.updatePublishStatus(botId, uid, spaceId, newStatus, newChannels);
        if (updateCount == 0) {
            log.warn("Bot offline update failed, record not found: botId={}, uid={}, spaceId={}", 
                    botId, uid, spaceId);
        } else {
            log.info("Bot offline update successful: botId={}, status={}, channels={}", 
                    botId, newStatus, newChannels);
        }
    }

    /**
     * Insert bot market record (used for first time publishing)
     * Sync complete data from chat_bot_base to chat_bot_market
     */
    private void insertChatBotMarketRecord(Integer botId, String uid, Long spaceId, Integer status, String channels) {
        // First query bot basic information
        ChatBotBase botBase = chatBotBaseMapper.selectById(botId);
        if (botBase == null) {
            throw new BusinessException(ResponseEnum.BOT_NOT_EXISTS);
        }

        // Create market record with complete data sync
        ChatBotMarket marketRecord = new ChatBotMarket();
        
        // Basic information
        marketRecord.setBotId(botId);
        marketRecord.setUid(uid);
        marketRecord.setBotName(botBase.getBotName());
        marketRecord.setBotDesc(botBase.getBotDesc());
        marketRecord.setAvatar(botBase.getAvatar());
        marketRecord.setBotType(botBase.getBotType());
        
        // Core configuration
        marketRecord.setPrompt(botBase.getPrompt());
        marketRecord.setPrologue(botBase.getPrologue());
        marketRecord.setVersion(botBase.getVersion());
        
        // Background images
        marketRecord.setPcBackground(botBase.getPcBackground());
        marketRecord.setAppBackground(botBase.getAppBackground());
        
        // Functional configuration
        marketRecord.setSupportContext(botBase.getSupportContext());
        
        // Market-specific fields
        marketRecord.setShowIndex(0); // Default not recommended
        
        // Status and channel management
        marketRecord.setBotStatus(status);
        marketRecord.setPublishChannels(channels);
        marketRecord.setIsDelete(0);
        marketRecord.setCreateTime(LocalDateTime.now());
        marketRecord.setUpdateTime(LocalDateTime.now());

        // Insert record
        int insertCount = chatBotMarketMapper.insert(marketRecord);
        if (insertCount == 0) {
            throw new BusinessException(ResponseEnum.BOT_UPDATE_FAILED);
        }

        log.info("Create bot market record with complete data sync: botId={}, status={}, channels={}", 
                botId, status, channels);
    }

    /**
     * Sync bot data from chat_bot_base to chat_bot_market (for existing records)
     * When re-publishing, sync all latest data to ensure consistency
     */
    private void syncBotDataToMarket(Integer botId, String uid, Long spaceId, Integer newStatus, String newChannels) {
        // Query latest bot data
        ChatBotBase botBase = chatBotBaseMapper.selectById(botId);
        if (botBase == null) {
            throw new BusinessException(ResponseEnum.BOT_NOT_EXISTS);
        }

        // Build update wrapper to sync all data fields
        com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper<ChatBotMarket> updateWrapper = 
                new com.baomidou.mybatisplus.core.conditions.update.UpdateWrapper<>();
        
        updateWrapper.eq("bot_id", botId)
                     .eq("uid", uid);

        // Sync all data fields from chat_bot_base to ensure data consistency
        updateWrapper.set("bot_name", botBase.getBotName())
                     .set("bot_desc", botBase.getBotDesc())
                     .set("avatar", botBase.getAvatar())
                     .set("bot_type", botBase.getBotType())
                     .set("prompt", botBase.getPrompt())
                     .set("prologue", botBase.getPrologue())
                     .set("version", botBase.getVersion())
                     .set("pc_background", botBase.getPcBackground())
                     .set("app_background", botBase.getAppBackground())
                     .set("support_context", botBase.getSupportContext())
                     .set("bot_status", newStatus)
                     .set("publish_channels", newChannels)
                     .set("update_time", LocalDateTime.now());

        int updateCount = chatBotMarketMapper.update(null, updateWrapper);
        if (updateCount == 0) {
            throw new BusinessException(ResponseEnum.BOT_UPDATE_FAILED);
        }

        log.info("Sync bot data to market successfully: botId={}, status={}, channels={}", 
                botId, newStatus, newChannels);
    }
}
