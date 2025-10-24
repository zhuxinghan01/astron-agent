package com.iflytek.astron.console.toolkit.entity.vo;

import com.alibaba.fastjson2.JSONObject;
import com.iflytek.astron.console.commons.entity.workflow.Workflow;
import lombok.Data;
import lombok.EqualsAndHashCode;

import java.util.List;

@EqualsAndHashCode(callSuper = true)
@Data
public class WorkflowVo extends Workflow {
    String address;
    String color;
    JSONObject ioInversion;
    String evalSetName;
    String sourceCode;
    Boolean bindAiuiAgent = false;
    List<String> inputExampleList;
    Boolean haQaNode = false;
    String version;
    /**
     * Voice intelligent agent configuration
     */
    String flowConfig;
}
