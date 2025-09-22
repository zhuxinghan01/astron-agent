package com.iflytek.stellar.console.commons.mapper.bot;

import com.baomidou.mybatisplus.core.mapper.BaseMapper;
import com.iflytek.stellar.console.commons.entity.bot.BotDetail;
import com.iflytek.stellar.console.commons.entity.bot.ChatBotBase;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;

@Mapper
public interface ChatBotBaseMapper extends BaseMapper<ChatBotBase> {
    BotDetail botDetail(Integer botId);

    List<ChatBotBase> selectByBotIds(@Param("botIds") List<Long> botIds);

}
