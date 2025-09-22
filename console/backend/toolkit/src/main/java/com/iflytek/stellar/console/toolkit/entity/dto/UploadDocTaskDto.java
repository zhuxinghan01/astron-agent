package com.iflytek.stellar.console.toolkit.entity.dto;

import com.iflytek.stellar.console.toolkit.entity.table.repo.UploadDocTask;
import lombok.Data;
import lombok.EqualsAndHashCode;

@EqualsAndHashCode(callSuper = true)
@Data
public class UploadDocTaskDto extends UploadDocTask {
    private String sourceId;
}
