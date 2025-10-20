package com.iflytek.astron.console.toolkit.task.scheduler;

import com.iflytek.astron.console.toolkit.entity.enumVo.DebugStatus;
import com.iflytek.astron.console.toolkit.entity.vo.rpa.DebugSession;
import com.iflytek.astron.console.toolkit.service.tool.RpaDebugService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Component
public class PollScheduler {

    private final RpaDebugService debugService;
    private final Map<String, Long> lastPollAt = new ConcurrentHashMap<>();

    public PollScheduler(RpaDebugService debugService) {
        this.debugService = debugService;
    }

    @Scheduled(fixedDelay = 500)
    public void tick() {
        long now = System.currentTimeMillis();
        for (DebugSession s : debugService.all()) {
            if (isFinal(s.getStatus()))
                continue;
            String key = s.getDebugId();
            long last = lastPollAt.getOrDefault(key, 0L);
            if (now - last >= s.getNextPollMs()) {
                lastPollAt.put(key, now);
                debugService.pollOnce(s, s.getApiToken());
            }
        }
    }

    private boolean isFinal(DebugStatus st) {
        return st == DebugStatus.SUCCEEDED || st == DebugStatus.FAILED || st == DebugStatus.CANCELED || st == DebugStatus.TIMEOUT;
    }
}
