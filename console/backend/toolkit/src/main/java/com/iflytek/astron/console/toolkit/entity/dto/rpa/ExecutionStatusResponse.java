package com.iflytek.astron.console.toolkit.entity.dto.rpa;

import com.alibaba.fastjson2.JSONObject;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

import java.util.Map;

@Data
public class ExecutionStatusResponse {
    private String code;
    private String msg;
    private Data data;

    public static class Data {
        private Execution execution;

        public Execution getExecution() {
            return execution;
        }

        public void setExecution(Execution execution) {
            this.execution = execution;
        }
    }

    public static class Execution {
        private String id;

        @JsonProperty("project_id")
        private String projectId;

        // PENDING / COMPLETED / FAILED
        private String status;

        private JSONObject parameters;

        private Map<String, Object> result;
        private Object error;

        @JsonProperty("exec_position")
        private String execPosition;

        private Integer version;

        @JsonProperty("user_id")
        private String userId;

        @JsonProperty("start_time")
        private String startTime;

        @JsonProperty("end_time")
        private String endTime;

        public String getId() {
            return id;
        }

        public void setId(String id) {
            this.id = id;
        }

        public String getProjectId() {
            return projectId;
        }

        public void setProjectId(String projectId) {
            this.projectId = projectId;
        }

        public String getStatus() {
            return status;
        }

        public void setStatus(String status) {
            this.status = status;
        }

        public JSONObject getParameters() {
            return parameters;
        }

        public void setParameters(JSONObject parameters) {
            this.parameters = parameters;
        }

        public Map<String, Object> getResult() {
            return result;
        }

        public void setResult(Map<String, Object> result) {
            this.result = result;
        }

        public Object getError() {
            return error;
        }

        public void setError(Object error) {
            this.error = error;
        }

        public String getExecPosition() {
            return execPosition;
        }

        public void setExecPosition(String execPosition) {
            this.execPosition = execPosition;
        }

        public Integer getVersion() {
            return version;
        }

        public void setVersion(Integer version) {
            this.version = version;
        }

        public String getUserId() {
            return userId;
        }

        public void setUserId(String userId) {
            this.userId = userId;
        }

        public String getStartTime() {
            return startTime;
        }

        public void setStartTime(String startTime) {
            this.startTime = startTime;
        }

        public String getEndTime() {
            return endTime;
        }

        public void setEndTime(String endTime) {
            this.endTime = endTime;
        }
    }

    public String getCode() {
        return code;
    }

    public void setCode(String code) {
        this.code = code;
    }

    public String getMsg() {
        return msg;
    }

    public void setMsg(String msg) {
        this.msg = msg;
    }

    public Data getData() {
        return data;
    }

    public void setData(Data data) {
        this.data = data;
    }
}
