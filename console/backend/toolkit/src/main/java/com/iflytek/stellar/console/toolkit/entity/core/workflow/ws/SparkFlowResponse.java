package com.iflytek.stellar.console.toolkit.entity.core.workflow.ws;


import com.iflytek.stellar.console.toolkit.entity.spark.Parameter;
import com.iflytek.stellar.console.toolkit.entity.spark.chat.Payload;
import lombok.Data;

@Data
public class SparkFlowResponse {
    SparkFlowResponseHeader header;
    Payload payload;
    Parameter parameter;
}
