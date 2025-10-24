package com.iflytek.astron.console.commons.dto.bot;

import lombok.Data;

public class TalkAgentCreateDto extends BotCreateForm {
    private TalkAgentConfigDto talkAgentConfigDto;

    public TalkAgentConfigDto getTalkAgentConfig() {
        return this.talkAgentConfigDto;
    }
}
