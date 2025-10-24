package com.iflytek.astron.console.commons.service.bot;

import com.alibaba.fastjson2.JSONObject;
import com.iflytek.astron.console.commons.dto.bot.BotCreateForm;
import com.iflytek.astron.console.commons.dto.bot.BotInfoDto;
import com.iflytek.astron.console.commons.entity.bot.BotTypeList;
import com.iflytek.astron.console.commons.entity.bot.ChatBotBase;
import jakarta.servlet.http.HttpServletRequest;

import java.util.List;

/**
 * @author wowo_zZ
 * @since 2025/9/9 20:24
 **/

public interface BotService {

    BotInfoDto getBotInfo(HttpServletRequest request, Integer botId, Long chatId, String workflowVersion);

    Boolean deleteBot(Integer botId);

    List<BotTypeList> getBotTypeList();

    BotInfoDto insertWorkflowBot(String uid, BotCreateForm bot, Long spaceId, Integer version);

    BotInfoDto insertBotBasicInfo(String uid, BotCreateForm bot, Long spaceId);

    ChatBotBase copyBot(String uid, Integer botId, Long spaceId);

    Boolean updateWorkflowBot(String uid, BotCreateForm bot, HttpServletRequest request, Long spaceId);

    Boolean updateBotBasicInfo(String uid, BotCreateForm bot, Long spaceId);

    void addMaasInfo(String uid, JSONObject maas, Integer botId, Long spaceId);

    void addV2Bot(String uid, Integer botId);
}
