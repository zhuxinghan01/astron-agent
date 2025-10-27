package com.iflytek.astron.console.hub.enums;

import com.iflytek.astron.console.commons.dto.bot.TalkAgentVCNDto;
import lombok.AllArgsConstructor;
import lombok.Getter;

import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

@Getter
@AllArgsConstructor
public enum TalkAgentVCNEnum {

    ZHIXING_NVSHENG("x5_lingyuyan_flow", "女", "[成熟,知性]", "普通话", "知性女声", 
            "生活没有标准答案，每个人都有自己的注脚。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/140308ef-1534-414e-80e9-28dcfb38ae39/1761310470644/1280X1280.PNG", 
            null),
    
    QINGXIN_NVSHENG("x5_lingxiaoyue_flow", "女", "[青年,清新]", "普通话", "清新女声", 
            "好久不见，你最近可好？ ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/8a2c98ae-13eb-4709-aaf5-a11f03075188/1761310472055/1280X1280%20%281%29.PNG", 
            null),
    
    ZHONGXING_NVSHENG("x4_lingyuzhao_oral", "女", "[青年,中性]", "普通话", "中性女声", 
            "你平时玩音乐吗？我说的可不是听网易云。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/4fee5dc7-7690-4064-b001-a8626078f0eb/1761310472871/1280X1280%20%282%29.PNG", 
            null),
    
    NEIXIANG_NVSHENG("x4_lingxiaoqi_em_v2", "女", "[青年,内向]", "普通话", "内向女声", 
            "抱歉，我是不是打扰到你了？ ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/35aeec32-9364-4f60-b6af-b1d14971d823/1761310474258/1280X1280%20%284%29.PNG", 
            "7"),
    
    GAOLENG_NVSHENG("x4_lingxiaoyun_talk", "女", "[成熟,高冷]", "普通话", "高冷女声", 
            "天下真有这样标致的人物！我今儿才算头一回见了！ ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/2c861aab-5eaf-498a-a948-d512a3891be4/1761310474917/1280X1280%20%285%29.PNG", 
            null),
    
    TIANZHEN_NVSHENG("x4_lingyouyou_oral", "女", "[儿童,天真]", "普通话", "天真女声", 
            "你在看什么呀？给我也瞧瞧。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/27644ee3-4d15-4e07-abc5-0b2bb78d8271/1761310475667/1280X1280%20%286%29.PNG", 
            null),
    
    CIXIANG_NVSHENG("x4_xiuying", "女", "[中老年,慈祥]", "普通话", "慈祥女声", 
            "我年轻的时候，就馋这一碗面。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/19b4cf08-9e36-44e8-b84e-df4b36206a29/1761310476476/1280X1280%20%287%29.PNG", 
            null),
    
    SHUANGZHI_NVSHENG("x4_xiaobei", "女", "[青年,爽直]", "东北话", "爽直女声", 
            "你瞅啥，你这几个月没洗澡了，埋了八汰的咋整。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/446b9b3c-f81c-4607-b9a2-a6cd93ff55fd/1761310477315/1280X1280%20%288%29.PNG", 
            null),
    
    QINQIE_NVSHENG("x4_TwCn_ZiWen_assist", "女", "[青年,亲切]", "台湾普通话", "亲切女声", 
            "不要这么机车，垃圾要丢到正确的位置。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/e203b0c9-0c64-4be6-a2a2-c340f32e7869/1761310478142/1280X1280%20%289%29.PNG", 
            null),
    
    RUANMENG_NVSHENG("x4_lingxiaoyao_anime", "女", "[青年,软萌]", "普通话", "软萌女声", 
            "也许只有在二次元的世界里，才有真正的美好存在吧。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/6899aea4-9e6a-44f7-8adf-65d61deae75b/1761310478952/1280X1280%20%2810%29.PNG", 
            null),
    
    WENROU_NVSHENG("x4_lingxiaoxuan_talk", "女", "[青年,温柔]", "普通话", "温柔女声", 
            "只有一个人在旅行时，才听得到自己的声音，它会告诉你，这世界比想象中的宽阔。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/0b6d5979-1d24-49ad-8de9-306be52cdc9d/1761310479747/1280X1280%20%2811%29.PNG", 
            null),
    
    YANGGUANG_NANSHENG("x4_lingfeichen_emo", "男", "[青年,阳光]", "普通话", "阳光男生", 
            "不要一个人玩手机，记得给我打电话。你不用改变自己，我来慢慢适应你。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/fafdb344-7cb1-47ed-af20-c01da7416773/1761310480412/1280X1280%20%2812%29.PNG", 
            "5"),
    
    CHENWEN_NANSHENG("x5_lingfeiyi_flow", "男", "[成熟,沉稳]", "普通话", "沉稳男声", 
            "晚上不要吃夜宵，对胃不好。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/6b777475-4d7b-446c-94eb-0c1dff94918e/1761310481070/1280X1280%20%2813%29.PNG", 
            null),
    
    REXUE_NANSHENG("x4_lingfeiyuan_gamecom", "男", "[青年,热血]", "普通话", "热血男声", 
            "露娜王也有技能放空的时候，但是就算技能放空我也还是露娜王。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/23348ee5-1b89-445b-ba3f-e525521e0449/1761310482480/1280X1280%20%2815%29.PNG", 
            null),
    
    CIXIANG_NANSHENG("x4_lingbosong", "男", "[中老年,慈祥]", "普通话", "慈祥男声", 
            "我泡的菊花茶温了，你趁热喝，解解乏。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/1969ecf5-b6f7-416e-9a99-15a52b347056/1761310483202/1280X1280%20%2816%29.PNG", 
            null),
    
    TIANZHEN_NANSHENG("x4_lingxiaowan_boy", "男", "[儿童,天真]", "普通话", "天真男声", 
            "我的奥特曼玩具找不到了，你帮我一起找好不好？ ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/b5dc162f-fa40-4049-be2e-540e23e408a0/1761310483942/1280X1280%20%2817%29.PNG", 
            null),
    
    GAOLENG_NANSHENG("x4_gaolengnanshen_talk", "男", "[青年,高冷]", "普通话", "高冷男声", 
            "关你什么事？赶紧给我闪开，不然别怪我不客气了！ ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/5c2c2a5a-1e08-4030-8da7-2a964dba0e1c/1761310484503/1280X1280%20%2818%29.PNG", 
            null),
    
    PIQI_NANSHENG("x4_piqihunhun_talk", "男", "[青年,痞气]", "普通话", "痞气男声", 
            "借你笔用用，别抠搜的！用完肯定还你，急啥？ ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/b93469ce-0911-4ce6-a4fc-88c506bd8545/1761310485176/1280X1280%20%2819%29.PNG", 
            null),
    
    TIANJIN_XIAOGE("x4_zijin_oral", "男", "[青年,方言]", "天津话", "天津小哥", 
            "介刚摊的煎饼果子，倍儿脆！你要不要也来一套？ ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/8fc4fffe-8966-4050-93bd-775f6c18669c/1761310485831/1280X1280%20%2820%29.PNG", 
            null),
    
    CIXING_NANSHENG("x5_lingfeiwen_flow", "男", "[青年,磁性]", "普通话", "磁性男声", 
            "今晚风有点凉，你出门时记得披件薄外套，别着凉 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/9d364d99-9981-40a2-a587-3106f9d724b0/1761310486428/1280X1280%20%2821%29.PNG", 
            null),
    
    NUANXIN_NVSHENG("x4_lingxiaoli_oral", "女", "[青年,暖心]", "普通话", "暖心女声", 
            "别总盯着屏幕啦，歇会儿眼睛，我给你剥了橘子。 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/6065f51d-d19b-4677-a03f-8573d723e096/1761310487094/1280X1280%20%2822%29.PNG", 
            null),
    
    DONGBEI_DAGE("x4_ziyang_oral", "男", "[青年,方言]", "东北话", "东北大哥", 
            "咱楼下新开的菜馆，菜码贼大，晚上一块儿整两口？ ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/9827db51-d31a-409e-a27a-c7b26ab687fb/1761310487802/1280X1280%20%2823%29.PNG", 
            null),
    
    XIAOYUN("x4_xiaoyuan", "女", "[青年,虚拟人]", "普通话", "晓云", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/98ff2676-74cc-49c8-ae90-f92531826962/1761310488471/1280X1280%20%2824%29.PNG", 
            null),
    
    YIFAN("x4_mingge", "男", "[青年,虚拟人]", "普通话", "伊凡", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/59eac390-2bc2-4c03-836f-5b4464cf20bf/1761310488988/1280X1280%20%2825%29.PNG", 
            null),
    
    XIAOXIAN("x4_lingxiaoyu_assist", "女", "[青年,虚拟人]", "普通话", "晓娴", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/c72effb2-ed60-4aa1-b4eb-290310cbffd4/1761310489480/1280X1280%20%2826%29.PNG", 
            null),
    
    LINNA("x4_EnUs_Lindsay_assist", "女", "[青年,虚拟人]", "普通话", "Linna", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/a1ba46e7-9665-46d6-81ea-52ecf7dfb538/1761310489953/1280X1280%20%2827%29.PNG", 
            null),
    
    SUSHI("x4_chaoge", "男", "[青年,虚拟人]", "普通话", "苏轼", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/fcd383f9-47eb-40a2-b887-97b1c59ead72/1761310490464/1280X1280%20%2828%29.PNG", 
            null),
    
    MUMU("f18f328_ttsclone-xfyousheng-ddivi", "女", "[青年,虚拟人]", "普通话", "沐沐", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/5eb21bf5-d963-478a-8020-6c48e1cb4741/1761310490931/1280X1280%20%2829%29.PNG", 
            null),
    
    DUODUO("x4_lingyouyou_oral", "女", "[青年,虚拟人]", "普通话", "朵朵", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/fa7c6cb7-24b4-4a49-934b-a1ec8f9118e6/1761310491398/1280X1280%20%2830%29.PNG", 
            null),
    
    ZHAOZHAO("5f2e7b1_ttsclone-xfyousheng-ydynu", "女", "[青年,虚拟人]", "普通话", "昭昭", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/20b33906-2ffb-41bd-93b3-a38ffd0c2c79/1761310492359/1280X1280%20%2832%29.PNG", 
            null),
    
    XIAOWEN("x4_xiaoguo", "女", "[青年,虚拟人]", "普通话", "晓雯", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/bc3e383d-9aca-49ac-a874-c2595eba99d5/1761310492820/1280X1280%20%2833%29.PNG", 
            null),
    
    XIAOYI("x4_lingxiaoqi_assist", "女", "[青年,虚拟人]", "普通话", "晓依", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/2139ac4b-c3f8-489e-a269-cf49896b94d6/1761310493320/1280X1280%20%2834%29.PNG", 
            null),
    
    CHENCHEN("x4_lingyouyou_oral", "女", "[青年,虚拟人]", "普通话", "辰辰", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/a584715b-4686-4ffd-8fa8-711ec6034505/1761310493819/1280X1280%20%2835%29.PNG", 
            null),
    
    XIAOMAN("x4_lingxiaoyao_anime", "女", "[青年,虚拟人]", "普通话", "小满", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/8b2ab1a3-431f-4094-a206-72694cacf47f/1761310495772/1280X1280%20%2839%29.PNG", 
            null),
    
    LIQINGZHAO("a050e71_ttsclone-xfyousheng-lbhge", "女", "[青年,虚拟人]", "普通话", "李清照", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/9dc65e8d-21ec-478d-8031-5592883cfdea/1761310496231/1280X1280%20%2840%29.PNG", 
            null),
    
    LINDAIYU("5f2e7b1_ttsclone-xfyousheng-ydynu", "女", "[青年,虚拟人]", "普通话", "林黛玉", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/2bb8c550-7c3d-44fc-87fb-1817997343f6/1761310496721/1280X1280%20%2841%29.PNG", 
            null),
    
    FENGYAN("8575648_ttsclone-xfyousheng-kssxv", "男", "[青年,虚拟人]", "普通话", "风晏", 
            "懂你所言，答你所问，我是你的讯飞星辰小助理 ", 
            "https://openres.xfyun.cn/xfyundoc/2025-10-24/81148ba9-65f0-4b23-a07e-d48fb9309d61/1761310497185/1280X1280%20%2842%29.PNG", 
            null);

    private final String vcn;
    private final String gender;
    private final String tag;
    private final String language;
    private final String vcnName;
    private final String example;
    private final String avatar;
    private final String emotion;


    public static List<TalkAgentVCNDto> getAllVCN() {
        return Arrays.stream(values())
                .map(vcnEnum -> new TalkAgentVCNDto(
                        vcnEnum.getVcn(),
                        vcnEnum.getGender(),
                        vcnEnum.getTag(),
                        vcnEnum.getLanguage(),
                        vcnEnum.getVcnName(),
                        vcnEnum.getExample(),
                        vcnEnum.getAvatar(),
                        vcnEnum.getEmotion()
                ))
                .collect(Collectors.toList());
    }
}
