package com.iflytek.astron.console.commons.service.bot;

import com.iflytek.astron.console.commons.constant.ResponseEnum;
import com.iflytek.astron.console.commons.dto.bot.TalkAgentHistoryDto;

public interface TalkAgentService {
    String getSignature();

    ResponseEnum saveHistory(String uid, TalkAgentHistoryDto talkAgentHistoryDto);
}
