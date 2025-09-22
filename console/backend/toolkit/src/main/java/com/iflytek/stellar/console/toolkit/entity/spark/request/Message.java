package com.iflytek.stellar.console.toolkit.entity.spark.request;

import com.iflytek.stellar.console.toolkit.entity.spark.Text;
import lombok.Data;

import java.util.List;

@Data
public class Message {
    List<Text> text;
}
