package com.iflytek.astron.console.commons.service.bot;

import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.dto.bot.TalkAgentHistoryDto;
import com.iflytek.astron.console.commons.dto.bot.TalkAgentUpgradeDto;
import jakarta.servlet.http.HttpServletRequest;

public interface TalkAgentService {
    String getSignature();

    ResponseEnum saveHistory(String uid, TalkAgentHistoryDto talkAgentHistoryDto);

    ResponseEnum upgradeWorkflow(Integer sourceId, String uid, Long spaceId, HttpServletRequest request, TalkAgentUpgradeDto talkAgentUpgradeDto);
}
