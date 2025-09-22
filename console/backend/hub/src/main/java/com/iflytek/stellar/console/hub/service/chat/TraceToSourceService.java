package com.iflytek.stellar.console.hub.service.chat;

import com.iflytek.stellar.console.commons.entity.chat.ChatRespModelDto;
import com.iflytek.stellar.console.commons.entity.chat.ChatTraceSource;

import java.util.List;

public interface TraceToSourceService {

    void respAddTrace(List<ChatRespModelDto> respList, List<ChatTraceSource> traceList);
}
