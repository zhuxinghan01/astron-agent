import React, { useEffect, useState } from 'react';
import { Button, message, Modal } from 'antd';
import { useNavigate } from 'react-router-dom';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
// import config from '@/config';
import {
  getApiCertInfo,
  getApiList,
  getApiInfo,
  getApiUsage,
  createApi,
  getApiHistory,
  getOrderList,
  getHasEditor,
} from '@/services/spark-common';
import { Select } from 'antd';

import backIcon from '@/assets/imgs/bot-center/back_createbot.svg';

import styles from './api.module.scss';

// 获取过去七天的日期，返回数组，格式为：2023-09-01
const getSevenDay = () => {
  const date = new Date();
  const arr: any[] = [];
  for (let i = 0; i < 7; i++) {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;
    const day = date.getDate() - i;
    arr.push(`${year}-${month}-${day}`);
  }
  return arr.reverse();
};
const OptionsDefault = {
  tooltip: {
    show: true,
  },
  grid: {
    top: 30,
    bottom: 30,
    left: 50,
    right: 40,
  },
  xAxis: {
    boundaryGap: false,
    data: getSevenDay(),
    type: 'category',
    axisLine: {
      show: false,
    },
    axisTick: {
      show: false,
    },
  },
  yAxis: {
    type: 'value',
    splitLine: {
      lineStyle: {
        type: 'dashed',
      },
    },
  },
  series: [
    {
      type: 'line',
      smooth: true,
      data: [0, 0, 0, 0, 0, 0, 0],
      lineStyle: {
        color: '#405DF9',
      },
      areaStyle: {
        color: '#405DF9',
        opacity: 0.25,
      },
      itemStyle: {
        color: '#405DF9',
      },
    },
  ],
};
const Divider = () => {
  return (
    <div className={styles.divider}>
      {[1, 2, 3, 4, 5, 6].map((_item, index) => {
        return <div key={index} className={styles.divider_circle} />;
      })}
    </div>
  );
};

export default function BotApi({ isOpenapi = false }: { isOpenapi?: any }) {
  const { t } = useTranslation();
  // 新增状态，标记是否已经获取过 API 列表
  const [hasFetchedApiList, setHasFetchedApiList] = useState<boolean>(false);
  const [searchParams] = useSearchParams();
  const [botId, setBotId]: any = useState('');
  // const [version, setVersion]:any = useState('');
  const navigate = useNavigate();
  const [isApiCertInfo, setIsApiCertInfo] = useState<boolean>(false);
  const [apiList, setApiList] = useState<any[]>([]);
  const [apiId, setApiId] = useState<any>(''); //appid
  const [apiInfo, setApiInfo] = useState<any>(null);
  const [apiUsage, setApiUsage] = useState<any>({});
  const [newsOption, setNewsOption] = useState<any>(OptionsDefault);
  const [apiHistoryType, setApiHistoryType] = useState<number>(1);
  const [freshCount, setFreshCount] = useState<number>(0); // 刷新页面数据
  const [loading, setLoading] = useState(false);
  const [listModalOpen, setListModalOpen] = useState(false);
  const [listModalData, setListModalData] = useState<any[]>([]); //订单列表
  const [publishBindId, setPublishBindId] = useState<any>(); // 发布绑定id
  const [publishBindIdLoading, setPublishBindIdLoading] = useState(false);
  const [SkipBindLoading, setSkipBindLoading] = useState(false);
  const [selectError, setSelectError] = useState(false); // Select 错误状态
  const [docUrl, setDocUrl] = useState<string>(); // 文档地址
  const [isShowOperateBtn, setIsShowOperateBtn] = useState<boolean>(false); // 是否显示操作按钮

  const createApiFn = async (publishBindId?: any, appId?: any) => {
    try {
      await createApi({ botId, appId: appId || apiId, publishBindId });
      setFreshCount(freshCount + 1);
      message.success('绑定成功');
      setListModalOpen(false);
      setPublishBindId(null);
      setSelectError(false); // 重置错误状态
    } catch (e: any) {
      message.error(e?.msg);
      setPublishBindIdLoading(false);
      setSkipBindLoading(false);
    } finally {
      setPublishBindIdLoading(false);
      setSkipBindLoading(false);
    }
  };
  //获取是否有权限在api页面进行修改
  const getHasEditorFn = async () => {
    const res: any = await getHasEditor();
    setIsShowOperateBtn(res);
  };
  const handleSkipBind = async () => {
    setSkipBindLoading(true);
    createApiFn();
  };
  const operateApi = async (appId?: any) => {
    try {
      setLoading(true);
      const res = await getOrderList();
      const data = res.map((item: any) => {
        return {
          value: item.id,
          label: item.name || item.appId,
        };
      });
      if (data.length > 0 && searchParams.get('version') !== '1') {
        setListModalData(data);
        setListModalOpen(true);
      } else {
        createApiFn(null, appId);
      }
    } catch (error: any) {
      message.error(error?.msg);
      setLoading(false);
    } finally {
      setLoading(false);
    }
  };

  //更新 or 绑定
  const handleBandApi = async () => {
    if (!isShowOperateBtn) {
      message.warning('您当前没有权限，请联系管理员！');
      return;
    }
    if (!apiId) return message.warning('请先绑定您的应用');
    //获取是否有未绑定的套餐
    operateApi(apiId);
  };
  //确认绑定
  const handleConfirmBandApi = async () => {
    if (!publishBindId) {
      setSelectError(true); // 设置错误状态
      return;
    }
    setSelectError(false); // 清除错误状态
    setPublishBindIdLoading(true);
    createApiFn(publishBindId);
  };

  //取消
  const handleCancel = () => {
    setListModalOpen(false);
    setLoading(false);
    setPublishBindId(null);
    setSelectError(false); // 重置错误状态
  };
  const updateApiFn = async (botId: any, appId: any) => {
    setApiId(appId);
    setBotId(botId);
    operateApi(appId);
  };
  const getApiHistoryFn = async (botId: any, type: number) => {
    const res = await getApiHistory(botId, type);
    if (res?.x?.length === 0) setNewsOption(OptionsDefault);
    else
      setNewsOption((pre: any) => {
        return {
          ...pre,
          xAxis: {
            ...pre.xAxis,
            data: res?.x || [],
          },
          series: [
            {
              ...pre.series[0],
              data: res?.y || [],
            },
          ],
        };
      });
  };
  const getApiUsageFn = async (id: any) => {
    const res = await getApiUsage(id);
    setApiUsage(res);
  };

  //检测是否实名认证
  const getApiCertInfoFn = async () => {
    const res = await getApiCertInfo();
    setIsApiCertInfo(res);
  };

  // 🎯 根据环境打开不同的控制台网址 -- NOTE: 开源应该不需要打开控制台吧
  // const getConsoleUrl = () => {
  //   const consoleBase = config.CONSOLE;
  //   const baseUrl = consoleBase.startsWith('//')
  //     ? `https:${consoleBase}`
  //     : consoleBase;
  //   return `${baseUrl}${baseUrl.endsWith('/') ? '' : '/'}app/create`;
  // };

  const getApiListFn = async () => {
    const res = await getApiList();
    const data = res.map((item: any) => {
      return {
        value: item.appId,
        label: item.appName || item.appId,
      };
    });
    setApiList(data);
  };
  const getAPiInfoFn = async (id: any) => {
    const res = await getApiInfo(id);
    setApiInfo(res);
  };
  // 是否认证
  useEffect(() => {
    getHasEditorFn();
    getApiCertInfoFn();
  }, []);

  useEffect(() => {
    if (searchParams.get('id')) {
      setBotId(searchParams.get('id'));
    }

    // NOTE: 指令型和工作流类型的智能体文档不同 -- 0715补充
    const url =
      searchParams.get('version') !== '1'
        ? 'https://www.xfyun.cn/doc/spark/Agent04-API%E6%8E%A5%E5%85%A5.html'
        : 'https://www.xfyun.cn/doc/spark/SparkAssistantAPI.html';
    setDocUrl(url);
  }, [searchParams]);

  useEffect(() => {
    if (isApiCertInfo) {
      if (apiList?.length) {
        getAPiInfoFn(botId);
        getApiUsageFn(botId);
      } else if (!hasFetchedApiList) {
        getApiListFn();
        setHasFetchedApiList(true);
      }
    }
  }, [isApiCertInfo, apiList, freshCount, hasFetchedApiList]);
  useEffect(() => {
    if (apiInfo) {
      getApiHistoryFn(botId, apiHistoryType);
    }
  }, [apiInfo, apiHistoryType, freshCount]);

  return (
    <section className={styles.api_swap}>
      <section className={styles.api_container}>
        <div className={styles.api_header}>
          <img
            src={backIcon}
            alt=""
            style={{ marginRight: '10px', cursor: 'pointer' }}
            // onClick={() => navigate('/botcenter/createbot', { replace: true })}
            onClick={() => navigate(-1)}
          />
          <span className={styles.api_header_title}>{t('botApi.botApi')}</span>
          <span className={styles.api_header_subtitle}>
            {t('botApi.botApiDesc')}
          </span>
        </div>
        <div className={styles.api_step}>
          <div className={styles.step}>
            <img
              src="https://aixfyun-cn-bj.xfyun.cn/bbs/75713.75546409925/cir.svg"
              alt=""
              className={styles.step_index}
            />
            <div className={styles.step_detail}>
              <span className={styles.title}>{t('botApi.botApiCert')}</span>
              <span className={styles.subtitle}>
                {t('botApi.botApiCertDesc')}
              </span>
              <span
                className={styles.fun}
                onClick={() => {
                  window.open('https://console.xfyun.cn/user/authentication');
                }}
              >
                {isApiCertInfo
                  ? t('botApi.botApiCertSuccess')
                  : t('botApi.botApiCertBtn')}
              </span>
            </div>
          </div>
          <Divider />
          <div className={styles.step}>
            <img
              src="https://aixfyun-cn-bj.xfyun.cn/bbs/84687.53848944922/cir2.svg"
              alt=""
              className={styles.step_index}
            />
            <div className={styles.step_detail}>
              <span className={styles.title}>{t('botApi.bindApp')}</span>
              <span className={styles.subtitle}>{t('botApi.bindAppDesc')}</span>
              <span
                className={styles.fun}
                onClick={() => {
                  if (!isShowOperateBtn) {
                    message.warning('您当前没有权限，请联系管理员！');
                    return;
                  }
                  // window.open(getConsoleUrl());
                }}
              >
                {t('botApi.createApi')} {' >'}
              </span>
            </div>
          </div>
          <Divider />
          <div className={styles.step}>
            <img
              src="https://aixfyun-cn-bj.xfyun.cn/bbs/72624.64595654579/cir3.svg"
              alt=""
              className={styles.step_index}
            />
            <div className={styles.step_detail}>
              <span className={styles.title}>{t('botApi.callService')}</span>
              <span className={styles.subtitle}>
                {t('botApi.callServiceDesc')}
              </span>
              <span
                className={styles.fun}
                onClick={() => {
                  window.open(docUrl);
                }}
              >
                {t('botApi.apiDoc')}
              </span>
            </div>
          </div>
        </div>
        <div className={styles.statistic}>
          <div className={styles.certified_card}>
            <div className={styles.certified_card_title}>
              <span>{t('botApi.apiCertInfo')}</span>
              <div
                onClick={() => {
                  window.open(docUrl);
                }}
              >
                {t('botApi.viewApiDoc')}
              </div>
            </div>
            <div className={styles.appid_box}>
              <div className={styles.appid_select}>
                {apiInfo && (
                  <>
                    <span className={styles.appid_select_title}>
                      {t('botApi.bindAppID')}
                    </span>
                    <span
                      className={styles.appid_select_appid}
                      title={apiInfo.appId}
                    >
                      {apiInfo && apiInfo.appId}
                    </span>

                    <span className={styles.appid_select_divide} />
                    <span className={styles.appid_select_title}>
                      {t('botApi.appName')}
                    </span>
                    <span
                      className={styles.appid_select_appid}
                      title={apiInfo?.appName}
                    >
                      {apiInfo && apiInfo.appName
                        ? apiInfo.appName
                        : t('botApi.unNamed')}
                    </span>
                    {searchParams.get('version') !== '1' &&
                      isShowOperateBtn && (
                        <Button
                          type="primary"
                          ghost
                          size="small"
                          loading={loading}
                          style={{
                            marginLeft: 30,
                            color: '#fff',
                            height: '30px',
                            lineHeight: '30px',
                            fontSize: '12px',
                          }}
                          onClick={() => updateApiFn(botId, apiInfo.appId)}
                        >
                          {t('botApi.updateBind')}
                        </Button>
                      )}
                  </>
                )}
                {!apiInfo && (
                  <>
                    <Select
                      showSearch
                      style={{ width: 192 }}
                      placeholder={t('botApi.selectApp')}
                      onChange={e => {
                        setApiId(e);
                      }}
                      options={apiList}
                      disabled={!isApiCertInfo}
                      filterOption={(input, option) =>
                        (option?.label ?? '').includes(input)
                      }
                      filterSort={(optionA, optionB) =>
                        (optionA?.label ?? '')
                          .toLowerCase()
                          .localeCompare((optionB?.label ?? '').toLowerCase())
                      }
                    />
                    {isApiCertInfo && (
                      <Button
                        type="primary"
                        ghost
                        size="small"
                        loading={loading}
                        style={{
                          marginLeft: 10,
                          color: '#fff',
                          height: '30px',
                          lineHeight: '30px',
                          fontSize: '12px',
                        }}
                        onClick={() => handleBandApi()}
                      >
                        {t('botApi.bindAppBtn')}
                      </Button>
                    )}
                  </>
                )}
              </div>
              {searchParams.get('version') !== '1' && (
                <div style={{ marginTop: '4px' }}>
                  <a
                    className={styles.appid_download}
                    href="https://openres.xfyun.cn/xfyundoc/2025-03-25/1fa7e299-25ab-4128-92c9-a56928caea49/1742887223777/workflow_openapi_demo_python.py.zip"
                  >
                    {t('botApi.pythonDemoDownload')}
                  </a>
                  <a
                    className={styles.appid_download}
                    href="https://openres.xfyun.cn/xfyundoc/2025-03-25/ae1c647f-9d9e-4bdf-b50a-7f5e683aa6ad/1742887220264/workflow_openapi_demo_java.java.zip"
                  >
                    {t('botApi.javaDemoDownload')}
                  </a>
                </div>
              )}
            </div>
            <div className={styles.certified_card_tips}>
              <span style={{ color: '#DE9B7C' }}>*</span>
              {t('botApi.bindAppTips')}
            </div>
            <img
              src="https://aixfyun-cn-bj.xfyun.cn/bbs/16415.126278163174/%E8%99%9A%E7%BA%BF.svg"
              alt=""
              className={styles.cer_divide}
            />
            <div className={`${styles.cer_info}`}>
              <span className={styles.info_label}>
                {t('botApi.serviceUrl')}：
              </span>
              <span
                className={styles.info_res}
                title={apiInfo?.serviceUrl ? apiInfo?.serviceUrl : null}
              >
                {apiInfo?.serviceUrl
                  ? apiInfo?.serviceUrl
                  : t('botApi.bindAppTips2')}
              </span>
            </div>
            <div className={`${styles.cer_info}`}>
              <span className={styles.info_label}>API Secret:</span>
              <span className={styles.info_res}>
                {apiInfo?.apiSecret || t('botApi.bindAppTips2')}
              </span>
            </div>
            <div className={`${styles.cer_info}`}>
              <span className={styles.info_label}>API Key：</span>
              <span className={styles.info_res}>
                {apiInfo?.apiKey || t('botApi.bindAppTips2')}
              </span>
            </div>
            {searchParams.get('version') !== '1' && (
              <div className={`${styles.cer_info}`}>
                <span className={styles.info_label}>API Flowid</span>
                <span className={styles.info_res}>
                  {apiInfo?.flowId || t('botApi.bindAppTips2')}
                </span>
              </div>
            )}
          </div>
          <div className={styles.right}>
            <div className={styles.statistic_card}>
              <div className={styles.statistic_data}>
                <img
                  src="https://aixfyun-cn-bj.xfyun.cn/bbs/21995.93819230774/1.png"
                  alt=""
                  className={styles.data_img}
                />
                <div className={styles.data_used_num}>
                  {'_ _'}
                  {/* {apiInfo ? apiUsage?.usedCount : '_ _'} */}
                </div>
                <div className={styles.data_title}>
                  {t('botApi.todayUsedTokenNum')}
                </div>
              </div>
              <div className={styles.statistic_divide} />
              <div className={styles.statistic_data}>
                <img
                  src="https://aixfyun-cn-bj.xfyun.cn/bbs/48258.37497568033/2.png"
                  alt=""
                  className={styles.data_img}
                />
                <div className={styles.data_used_num}>
                  {'_ _'}
                  {/* {apiInfo ? apiUsage?.left : '_ _'} */}
                </div>
                <div className={styles.data_title}>
                  {t('botApi.remainTokenNum')}
                </div>
              </div>
              <div className={styles.statistic_divide} />
              <div className={styles.statistic_data}>
                <img
                  src="https://aixfyun-cn-bj.xfyun.cn/bbs/48258.37497568033/2.png"
                  alt=""
                  className={styles.data_img}
                />
                <div className={styles.data_used_num}>
                  {'_ _'}
                  {/* {apiInfo ? apiUsage?.conc : '_ _'} */}
                </div>
                <div className={styles.data_title}>QPS</div>
              </div>
            </div>
            <div className={styles.statistic_tips}>
              <div className={styles.statistic_tips_title}>
                {t('botApi.warmTips')}
              </div>
              <ul className={styles.statistic_tips_lists}>
                {/* <li>
                  每个智能体API有1000万token的调用量，如需更多调用量或扩容QPS，请
                  <img
                    src="https://1024-cdn.xfyun.cn/2022_1024%2Fcms%2F16914170178415047%2F1.png"
                    alt=""
                  />
                  <span>购买增量套餐包</span>{' '}
                  <span
                    onClick={() => {
                      window.open(
                        'https://console.xfyun.cn/workorder/commit?category=6f96f0b975df464d87bdf1529848b779&tid=7f5fd4f0d0884f8398f73a7fd9fb1b48&title=%E6%98%9F%E7%81%AB%E5%8A%A9%E6%89%8BAPI-%E5%90%88%E4%BD%9C%E5%92%A8%E8%AF%A2&categoryName=%E6%98%9F%E7%81%AB%E5%8A%A9%E6%89%8BAPI&tname=%E5%90%88%E4%BD%9C%E5%92%A8%E8%AF%A2&id=Spark'
                      );
                    }}
                  >
                    点击填写工单
                  </span>
                </li> */}
                <li>{t('botApi.apiKeyWarn')}</li>
              </ul>
            </div>
          </div>
        </div>
        <Modal
          open={listModalOpen}
          onCancel={() => {
            handleCancel();
          }}
          title={t('botApi.modal.title')}
          width={500}
          centered
          footer={
            <>
              <Button
                onClick={() => handleSkipBind()}
                color="default"
                disabled={publishBindIdLoading}
                loading={SkipBindLoading}
              >
                {t('botApi.modal.skip')}
              </Button>
              <Button
                type="primary"
                onClick={() => handleConfirmBandApi()}
                disabled={publishBindIdLoading}
                loading={publishBindIdLoading}
              >
                {t('botApi.modal.confirm')}
              </Button>
            </>
          }
        >
          <div className={styles.modal_tips}>{t('botApi.modal.tips')}</div>
          <Select
            options={listModalData}
            style={{
              width: '100%',
              marginBottom: 12,
            }}
            className={selectError ? 'my-select-error' : ''}
            onChange={e => {
              setPublishBindId(e);
              setSelectError(false); // 选择后清除错误状态
            }}
            value={publishBindId}
            placeholder={t('botApi.modal.selectOrder')}
            status={selectError ? 'error' : undefined}
          ></Select>
        </Modal>
      </section>
    </section>
  );
}
