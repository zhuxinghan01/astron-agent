package com.iflytek.astron.console.toolkit.entity.enumVo;

/**
 * RPA调试任务状态
 */
public enum DebugStatus {
    // local creation
    CREATED,
    // Received ExecutionId
    SUBMITTED,
    // RPA PENDING Running
    RUNNING,
    // RPA COMPLETED
    SUCCEEDED,
    // RPA FAILED Or local failure
    FAILED,
    // (Reserved, if later supported to be cancelled)
    CANCELED,
    // Attempt again after query failure
    RETRYING,
    // timeout
    TIMEOUT
}
