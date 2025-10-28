package com.iflytek.astron.console.commons.dto.bot;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TalkAgentVCNDto {
    private String vcn;
    private String gender;
    private String tag;
    private String language;
    private String vcnName;
    private String example;
    private String avatar;
    private String emotion;
}
