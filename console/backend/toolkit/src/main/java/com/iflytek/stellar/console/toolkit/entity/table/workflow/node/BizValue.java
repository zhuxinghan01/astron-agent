package com.iflytek.stellar.console.toolkit.entity.table.workflow.node;


import lombok.Data;

@Data
public class BizValue {
    String type;
    Object content;
    String contentErrMsg;
}
