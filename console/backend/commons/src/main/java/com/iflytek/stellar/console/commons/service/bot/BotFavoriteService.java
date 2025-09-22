package com.iflytek.stellar.console.commons.service.bot;


import com.iflytek.stellar.console.commons.dto.bot.BotFavoritePageDto;
import com.iflytek.stellar.console.commons.entity.bot.BotMarketForm;

import java.util.List;

public interface BotFavoriteService {

    BotFavoritePageDto selectPage(BotMarketForm botMarketForm, String uid, String langCode);

    void create(String uid, Integer botId);

    void delete(String uid, Integer botId);

    int getFavoriteNumByBotId(Integer botId);

    List<Integer> list(String uid);
}
