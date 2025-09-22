package com.iflytek.stellar.console.toolkit.entity.core.workflow;


import com.iflytek.stellar.console.toolkit.entity.core.workflow.node.NodeData;
import lombok.Data;

@Data
public class Node {
    String id;
    NodeData data;
}
