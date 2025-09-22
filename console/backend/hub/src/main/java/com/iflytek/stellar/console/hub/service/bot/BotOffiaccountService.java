package com.iflytek.stellar.console.hub.service.bot;

import com.iflytek.stellar.console.hub.entity.BotOffiaccount;

import java.util.List;

public interface BotOffiaccountService {

    List<BotOffiaccount> getAccountList(String uid);

}
