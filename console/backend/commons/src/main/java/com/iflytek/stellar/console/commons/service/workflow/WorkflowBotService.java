package com.iflytek.stellar.console.commons.service.workflow;

import com.iflytek.stellar.console.commons.entity.workflow.CloneSynchronize;

public interface WorkflowBotService {
    Integer massCopySynchronize(CloneSynchronize synchronize);
}
