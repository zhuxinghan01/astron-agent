package com.iflytek.stellar.console.toolkit.entity.spark;


import lombok.Data;

@Data
public class SparkApiProtocol {
    Header header;
    Parameter parameter;
    Payload payload;
}
