package com.iflytek.astron.console.commons.dto.bot;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TalkAgentVCNDto {
    private String vcnName;
    private String gender;
    private List<String> language;
    private String vcn;
    private String avatar;
}

