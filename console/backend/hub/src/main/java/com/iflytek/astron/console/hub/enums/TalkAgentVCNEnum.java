package com.iflytek.astron.console.hub.enums;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.Arrays;
import java.util.List;

@Getter
@AllArgsConstructor
public enum TalkAgentVCNEnum {

    WENROU_TIANMEI("温柔甜妹", "女", Arrays.asList("普通话"), "x5_zrr_MR", ""),
    YANGGUANG_NVHAI("阳光女孩", "女", Arrays.asList("普通话"), "x5_lingyuyan_max", ""),
    LINJIA_SHAONV("邻家少女", "女", Arrays.asList("普通话"), "x5_lingxiaoyue_flow", ""),
    WENNUAN_QINGNIAN("温暖青年", "男", Arrays.asList("普通话"), "x5_lingfeiyi_flow", ""),
    TIANJIN_XIAOGE("天津小哥", "男", Arrays.asList("天津话"), "x4_zijin_oral", ""),
    CIXING_NANSHENG("磁性男声", "男", Arrays.asList("普通话"), "x5_lingfeiwen_oral", ""),
    NUANXIN_XUEJIE("暖心学姐", "女", Arrays.asList("普通话"), "x4_lingxiaoli_oral", ""),
    KEAI_TONGSHENG("可爱童声", "女", Arrays.asList("孩子音"), "x4_lingyouyou_oral", ""),
    DONGBEI_DAGE("东北大哥", "男", Arrays.asList("东北话"), "x4_ziyang_oral", "");

    private final String vcnName;
    private final String gender;
    private final List<String> language;
    private final String vcn;
    private final String avatar;

    public static List<TalkAgentVCNEnum> getAllVCN() {
        return Arrays.asList(values());
    }
}
