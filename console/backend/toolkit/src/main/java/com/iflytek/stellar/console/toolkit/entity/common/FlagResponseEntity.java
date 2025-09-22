package com.iflytek.stellar.console.toolkit.entity.common;

import lombok.Data;

@Data
public class FlagResponseEntity {
    Boolean flag;
    Integer code;
    String desc;
    Object count;
    Object data;
}
