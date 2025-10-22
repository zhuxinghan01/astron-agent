package com.iflytek.astron.console.toolkit.entity.dto.rpa;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.validation.constraints.NotBlank;
import lombok.Data;

import java.util.Map;

@Data
public class StartReq {
    @NotBlank
    public String projectId;
    public String execPosition = "EXECUTOR";
    // 可空，默认 RPA 当前启用版本
    public Integer version;
    public Map<String, Object> params = Map.of();
}
