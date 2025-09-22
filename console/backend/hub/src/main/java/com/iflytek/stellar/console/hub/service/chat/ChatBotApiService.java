package com.iflytek.stellar.console.hub.service.chat;

import com.iflytek.stellar.console.commons.dto.bot.ChatBotApi;

import java.util.List;

public interface ChatBotApiService {

    List<ChatBotApi> getBotApiList(String uid);

}
