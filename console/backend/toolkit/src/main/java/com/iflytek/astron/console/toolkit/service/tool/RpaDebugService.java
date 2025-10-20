package com.iflytek.astron.console.toolkit.service.tool;

import com.iflytek.astron.console.toolkit.entity.dto.rpa.ExecutionStatusResponse;
import com.iflytek.astron.console.toolkit.entity.enumVo.DebugStatus;
import com.iflytek.astron.console.toolkit.entity.vo.rpa.DebugSession;
import com.iflytek.astron.console.toolkit.handler.RpaHandler;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;

/**
 * @Author clliu19
 * @Date: 2025/10/17 14:04
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class RpaDebugService {
    private final RpaHandler rpaHandler;
    private final Map<String, DebugSession> sessions = new ConcurrentHashMap<>();
    private final Map<String, List<Consumer<DebugSession>>> listeners = new ConcurrentHashMap<>();

    public DebugSession start(String projectId, Integer version, String execPosition, Map<String, Object> params, String tokenOverride) {
        DebugSession s = new DebugSession(projectId, version, execPosition, params, tokenOverride,
                3000, 1000);
        sessions.put(s.getDebugId(), s);

        try {
            String executionId = rpaHandler.executeAsync(projectId, execPosition, params, version, tokenOverride);
            s.setExecutionId(executionId);
            s.setStatus(DebugStatus.SUBMITTED);
            s.setMessage("submitted");
            emit(s);
        } catch (Exception e) {
            s.setStatus(DebugStatus.FAILED);
            s.setMessage("execute-async failed: " + e.getMessage());
            emit(s);
        }
        return s;
    }

    public DebugSession get(String debugId) {
        return sessions.get(debugId);
    }

    public Collection<DebugSession> all() {
        return sessions.values();
    }

    public void onUpdate(String debugId, Consumer<DebugSession> cb) {
        listeners.computeIfAbsent(debugId, k -> Collections.synchronizedList(new ArrayList<>())).add(cb);
    }

    public void offAll(String debugId) {
        listeners.remove(debugId);
    }

    private void emit(DebugSession s) {
        List<Consumer<DebugSession>> ls = listeners.get(s.getDebugId());
        if (ls != null) {
            for (Consumer<DebugSession> cb : ls)
                cb.accept(s);
        }
    }

    /**
     * 被 PollScheduler 调用：检查状态并更新
     */
    public void pollOnce(DebugSession s, String tokenOverride) {
        if (s == null)
            return;
        if (isFinal(s.getStatus()))
            return;

        // 生命周期到期
        if (s.isExpired()) {
            s.setStatus(DebugStatus.TIMEOUT);
            s.setMessage("Timeout after " + 3000 + "s");
            emit(s);
            return;
        }

        // 还没拿到 executionId，跳过
        if (s.getExecutionId() == null)
            return;

        try {
            ExecutionStatusResponse.Execution ex = rpaHandler.getExecution(s.getExecutionId(), tokenOverride);
            String rpaStatus = ex.getStatus();
            // RPA 状态映射
            if ("PENDING".equalsIgnoreCase(rpaStatus)) {
                s.setStatus(DebugStatus.RUNNING);
                s.setMessage("RPA PENDING");
                // 运行中逐步增大间隔（上限）
                long next = Math.min((long) (s.getNextPollMs() * 1.4), 15000);
                s.setNextPollMs(next);
            } else if ("COMPLETED".equalsIgnoreCase(rpaStatus)) {
                s.setStatus(DebugStatus.SUCCEEDED);
                s.setMessage("RPA COMPLETED");
            } else if ("FAILED".equalsIgnoreCase(rpaStatus)) {
                s.setStatus(DebugStatus.FAILED);
                String msg = (ex.getError() != null)
                        ? String.valueOf(ex.getError())
                        : "RPA FAILED";
                s.setMessage(msg);
            } else {
                s.setStatus(DebugStatus.RETRYING);
                s.setMessage("Unknown status: " + rpaStatus);
            }
            emit(s);
        } catch (Exception e) {
            log.error("poll once error e = ", e);
            s.setStatus(DebugStatus.RETRYING);
            s.setMessage("query failed: " + e.getMessage());
            int r = s.incRetries();
            long backoff = Math.min((long) (1000 * Math.pow(1.8, r)), 15000);
            s.setNextPollMs(backoff);
            emit(s);
        }
    }

    private boolean isFinal(DebugStatus st) {
        return st == DebugStatus.SUCCEEDED || st == DebugStatus.FAILED || st == DebugStatus.CANCELED || st == DebugStatus.TIMEOUT;
    }

    // 用于 SSE 输出的轻量 Map
    public Map<String, Object> toView(DebugSession s) {
        Map<String, Object> m = new LinkedHashMap<>();
        m.put("debugId", s.getDebugId());
        m.put("executionId", s.getExecutionId());
        m.put("status", s.getStatus().name());
        m.put("message", s.getMessage());
        m.put("progress", s.getProgress());
        m.put("updatedAt", s.getUpdatedAt().toString());
        return m;
    }
}
