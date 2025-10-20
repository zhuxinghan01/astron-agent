package com.iflytek.astron.console.toolkit.entity.dto.rpa;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;


@Data
public class ExecuteAsyncResponse {
    private String code;
    private String msg;
    private Data data;


    public static class Data {
        @JsonProperty("executionId")
        private String executionId;

        public String getExecutionId() {
            return executionId;
        }

        public void setExecutionId(String executionId) {
            this.executionId = executionId;
        }
    }
}
