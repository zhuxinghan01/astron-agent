package com.iflytek.stellar.console.hub.service.chat;


import com.iflytek.stellar.console.commons.entity.chat.ChatListCreateResponse;

public interface ChatRestartService {
    ChatListCreateResponse createNewTreeIndexByRootChatId(Long chatId, String uid, String chatListName);
}
