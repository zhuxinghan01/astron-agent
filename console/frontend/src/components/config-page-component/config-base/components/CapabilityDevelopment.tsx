import React, { useState, useRef, useEffect } from 'react';
import {
  Input,
  Tooltip,
  Switch,
  Modal,
  Button,
  message,
  Checkbox,
  Spin,
} from 'antd';
import { typeList } from '@/constants';
import {
  generateInputExample,
  listRepos,
  generatePrologue,
} from '@/services/spark-common';
import { placeholderText } from '@/components/bot-center/edit-bot/placeholder';
import { localeConfig } from '@/locales/localeConfig';
import { useSparkCommonStore } from '@/store/spark-store/spark-common';
import { useLocaleStore } from '@/store/spark-store/locale-store';
import SpeakerModal, { VcnItem } from '@/components/speaker-modal';
import UploadBackgroundModal from '@/components/upload-background';
import Personality from './personality-component';
import { RightOutlined, QuestionCircleOutlined } from '@ant-design/icons';

import settingFile from '@/assets/imgs/sparkImg/icon_bot_setting_file.png';
import settingKaichangbai from '@/assets/imgs/sparkImg/icon_bot_setting_kaichangbai.png';
import plugin from '@/assets/imgs/sparkImg/icon_bot_setting_plugin.png';
import del from '@/assets/imgs/knowledge/icon_chat_dropdown_del.png';
import arrowUp from '@/assets/imgs/sparkImg/arrowUp.png';
import arrowDown from '@/assets/imgs/sparkImg/arrowDown.png';
import aiGenerate from '@/assets/imgs/sparkImg/ai-generate.png';
import fileImg from '@/assets/imgs/bot-center/file.svg';
import closeImg from '@/assets/imgs/bot-center/close.svg';
import autoInputExamplesLoadingIcon from '@/assets/imgs/bot-center/autoInputExamplesLoadingIcon.svg';
import codeIcon from '@/assets/imgs/plugin/code.svg'; // 代码图标
import netIcon from '@/assets/imgs/plugin/network.svg'; // 网络图标
import genPicIcon from '@/assets/imgs/plugin/gen-pic.svg'; // 图片图标
import { useTranslation } from 'react-i18next';

import styles from './CapabilityDevelopment.module.scss';
import cls from 'classnames';
import { CheckboxChangeEvent } from 'antd/es/checkbox';

const { TextArea } = Input;

interface CapabilityDevelopmentProps {
  botCreateActiveV: any;
  setBotCreateActiveV: (v: any) => void;
  baseinfo: any;
  detailInfo: any;
  prompt: any;
  prologue: any;
  setPrologue: (v: any) => void;
  inputExample: string[];
  setInputExample: (v: string[]) => void;
  choosedAlltool: any;
  setChoosedAlltool: (v: any) => void;
  selectSource: any[];
  setSelectSource: (v: any[]) => void;
  supportContextFlag: boolean;
  setSupportContextFlag: (v: boolean) => void;
  tools: any[];
  setTools: (v: any[]) => void;
  files: any[];
  tree: any[];
  setTree: (v: any[]) => void;
  conversation: boolean;
  setConversation: (v: boolean) => void;
  multiModelDebugging: boolean;
  growOrShrinkConfig: any;
  setGrowOrShrinkConfig: (v: any) => void;
  personalityData: any;
  setPersonalityData: (v: any) => void;
  model: string;
  vcnList: VcnItem[];
}

const CapabilityDevelopment: React.FC<CapabilityDevelopmentProps> = props => {
  const {
    botCreateActiveV,
    setBotCreateActiveV,
    baseinfo,
    detailInfo,
    prompt,
    prologue,
    setPrologue,
    inputExample,
    setInputExample,
    choosedAlltool,
    setChoosedAlltool,
    selectSource,
    setSelectSource,
    supportContextFlag,
    setSupportContextFlag,
    tools,
    setTools,
    files,
    tree,
    setTree,
    conversation,
    setConversation,
    multiModelDebugging,
    growOrShrinkConfig,
    setGrowOrShrinkConfig,
    personalityData,
    setPersonalityData,
    model,
    vcnList,
  } = props;

  const backgroundImg = useSparkCommonStore(state => state.backgroundImg);
  const backgroundImgApp = useSparkCommonStore(state => state.backgroundImgApp);
  const { locale: localeNow } = useLocaleStore();

  const [uploadBackgroundModalVisible, setUploadBackgroundModalVisible] =
    useState(false);
  const { t } = useTranslation();
  const [shiliLoading, setShiliLoading] = useState(false);
  const [disList, setDisList]: any = useState([]);
  const [xieyi, setXieyi] = useState(true);
  const [showSpeakerModal, setShowSpeakerModal] = useState(false);
  const [inputExampFlag, setInputExampFlag] = useState(false);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const [openingRemarksModal, setOpeningRemarksModal] = useState(false);
  const [playing, setPlaying] = useState(false);
  const [visible, setVisible] = useState(false);
  const [dataSource, setDataSource] = useState<any>([]);
  const [isFresh, setIsFresh] = useState(false);
  const [inputExampleLoading, setInputExampleLoading] =
    useState<boolean>(false);
  const botTypeValue = 10;
  const promptNameList = [
    (localeConfig as any)?.[localeNow]?.roleSetting,
    (localeConfig as any)?.[localeNow]?.targetTasks,
    (localeConfig as any)?.[localeNow]?.needDescription,
  ];
  const [promptStructList, setPromptStructList] = useState<
    { promptKey: string; promptValue: string; id: number }[]
  >([]);
  const requestDescribe = t(
    'configBase.CapabilityDevelopment.requireCreativeNovelty'
  );
  const targetTask = t(
    'configBase.CapabilityDevelopment.pleaseWriteACreativeCommercialCopywriting'
  );
  const setRole = t(
    'configBase.CapabilityDevelopment.youAreAComprehensiveCopywriter'
  );
  const botDesc = 'wode';
  const name = '123';

  /**
   * 设置助手发音人
   */
  const setBotCreateVcn = (vcn: { cn: string }) => {
    setBotCreateActiveV({
      cn: vcn.cn,
    });
  };
  const onChecked = (e: CheckboxChangeEvent) => {
    setXieyi(e.target.checked);
  };

  /**
   * 渲染助手发音人
   */
  const renderBotVcn = () => {
    const vcnObj =
      vcnList.find((item: VcnItem) => item.voiceType === botCreateActiveV.cn) ||
      vcnList[0];

    return (
      <>
        {vcnObj ? (
          <>
            <img
              className="w-7 h-7 mr-1 rounded-full"
              src={vcnObj?.coverUrl}
              alt=""
            />
            <span title={vcnObj?.name}>
              {localeNow === 'en'
                ? vcnObj?.modelManufacturer
                  ? vcnObj?.modelManufacturer
                  : vcnObj?.name
                : vcnObj?.name}
            </span>
            <div
              style={{ marginLeft: '3px' }}
              className={styles.right_outline_wrap}
            >
              <RightOutlined style={{ color: '#A0A6AF', fontSize: 12 }} />
            </div>
          </>
        ) : (
          <>
            <img
              className={'w-[14px] h-3 mt-1.5 mr-1.5'}
              src={
                'https://openres.xfyun.cn/xfyundoc/2024-05-13/6c7b581a-e2f1-43fc-a73f-f63307df8150/1715581373857/1123213.png'
              }
              alt=""
            />
            {t('configBase.CapabilityDevelopment.selectPronouncer')}
          </>
        )}
      </>
    );
  };
  /**
   * AI生成输入示例
   */
  const getInputExamples = () => {
    if (!botDesc || !name || !setRole || !targetTask || !requestDescribe) {
      message.error(
        t(
          'configBase.CapabilityDevelopment.pleaseFillInAgentNameFunctionDescriptionAndAgentInstruction'
        )
      );
      return;
    }
    const botCommand = [
      {
        promptKey: promptNameList[0],
        promptValue: setRole,
      },
      {
        promptKey: promptNameList[1],
        promptValue: targetTask,
      },
      {
        promptKey: promptNameList[2],
        promptValue: requestDescribe,
      },
      ...promptStructList,
    ];

    setInputExampleLoading(true);
    generateInputExample({
      botName: baseinfo.botName,
      botDesc: baseinfo.botDesc,
      prompt: prompt,
    })
      .then((res: any) => {
        if (res && res.length === 3) setInputExample(res);
        else
          message.error(
            t('configBase.CapabilityDevelopment.generateFailedPleaseTryAgain')
          );
        setInputExampleLoading(false);
      })
      .catch(err => {
        err?.msg && message.error(err.msg);
        setInputExampleLoading(false);
      });
  };

  function deleteTool(toolId: string) {
    const newTools = tools.filter((item: any) => item.toolId !== toolId);
    setTools(newTools);
  }

  function deleteFile(record: any) {
    if (record.nodeType !== 0) {
      const newTree = deleteNodeById(tree, record.id);
      setTree(JSON.parse(JSON.stringify(newTree)));
    } else {
      const newTree = tree.filter((item: any) => item.id !== record.id);
      setTree(JSON.parse(JSON.stringify(newTree)));
    }
  }

  function deleteNodeById(tree: any, targetId: string) {
    // 递归函数用于在树中查找并删除节点
    function findAndDelete(node: any) {
      if (node.id === targetId) {
        return null; // 找到目标ID，返回null表示删除节点
      }

      if (node.files && node.files.length > 0) {
        node.files = node.files
          .map((child: any) => findAndDelete(child))
          .filter(Boolean);
      }

      if (node.nodeType !== 2 && node.files && node.files.length === 0) {
        return null;
      }

      return node;
    }

    // 在根节点调用递归函数
    const modifyTree = {
      files: [...tree],
    };
    const newTree = findAndDelete(modifyTree);

    return newTree ? newTree.files : [];
  }

  useEffect(() => {
    inputExample.forEach((item, index) => {
      if (item) {
        return setInputExampFlag(true);
      }
    });
    if (prologue) {
      setConversation(true);
    }
    listRepos().then((res: any) => {
      setDataSource(res?.pageData);
    });
  }, []);

  useEffect(() => {
    const arr: any = [];
    dataSource.forEach((item: any) => {
      if (item.checked) {
        arr.push(item);
      }
    });
    setDisList(arr);
  }, [dataSource]);

  return (
    <div
      className="flex-1  overflow-auto pr-6"
      ref={containerRef}
      style={{
        padding: multiModelDebugging ? '' : '0 24px',
        borderLeft: multiModelDebugging ? '' : '1px solid #E2E8FF',
        marginTop: multiModelDebugging ? 24 : 0,
      }}
    >
      <div className="flex items-center justify-between mt-6">
        <div className=" w-full">
          <div className="flex items-center" style={{ marginBottom: '20px' }}>
            {multiModelDebugging && (
              <img
                src={growOrShrinkConfig?.tools ? arrowDown : arrowUp}
                className="w-[16px] h-[16px] mr-2 cursor-pointer"
                alt=""
                onClick={() =>
                  setGrowOrShrinkConfig({
                    ...growOrShrinkConfig,
                    tools: !growOrShrinkConfig.tools,
                  })
                }
              />
            )}
            <img src={plugin} className="w-6 h-6" alt="" />
            <span className="ml-2 text-[#D84516] font-medium">
              {t('configBase.CapabilityDevelopment.capability')}
            </span>
          </div>
          <div
            className="flex justify-between items-center border-b border-[#E9EFF6]"
            style={{
              padding: '8px 20px 12px 20px',
            }}
          >
            <div className="flex gap-2 items-center">
              <img src={netIcon} alt="" className="w-[16px] h-[16px]" />
              <span className="text-sm font-medium">
                {t('configBase.CapabilityDevelopment.internetSearch')}
              </span>
            </div>
            <Switch
              className="list-switch config-switch"
              defaultChecked={
                detailInfo.openedTool?.indexOf('ifly_search') !== -1
              }
              onChange={checked => {
                choosedAlltool.ifly_search = checked;
                setChoosedAlltool(choosedAlltool);
              }}
            />
          </div>
          <div
            className="flex justify-between items-center border-b border-[#E9EFF6]"
            style={{
              padding: '8px 20px 12px 20px',
            }}
          >
            <div className="flex gap-2 items-center">
              <img src={genPicIcon} alt="" className="w-[16px] h-[16px]" />
              <span className="text-sm font-medium">
                {t('configBase.CapabilityDevelopment.AIDraw')}
              </span>
            </div>
            <Switch
              className="list-switch config-switch"
              defaultChecked={
                detailInfo.openedTool?.indexOf('text_to_image') !== -1
              }
              onChange={checked => {
                choosedAlltool.text_to_image = checked;
                setChoosedAlltool(choosedAlltool);
              }}
            />
          </div>
          <div
            className="flex justify-between items-center border-b border-[#E9EFF6]"
            style={{
              padding: '8px 20px 12px 20px',
            }}
          >
            <div className="flex gap-2 items-center">
              <img src={codeIcon} alt="" className="w-[16px] h-[16px]" />
              <span className="text-sm font-medium">
                {t('configBase.CapabilityDevelopment.codeGeneration')}
              </span>
            </div>
            <Switch
              className="list-switch config-switch"
              defaultChecked={
                detailInfo.openedTool?.indexOf('codeinterpreter') !== -1
              }
              onChange={checked => {
                choosedAlltool.codeinterpreter = checked;
                setChoosedAlltool(choosedAlltool);
              }}
            />
          </div>
        </div>
      </div>
      {growOrShrinkConfig.tools && tools.length > 0 && (
        <div className="mt-1.5 w-full overflow-auto max-h-[300px]">
          {tools.map((item: any, index: number) => (
            <div
              key={index}
              className="flex items-center px-5 py-3 border-b border-[#E2E8FF]"
            >
              <Tooltip
                title={
                  item.isPublic
                    ? t('configBase.CapabilityDevelopment.officialPlugin')
                    : t('configBase.CapabilityDevelopment.personalPlugin')
                }
                overlayClassName="black-tooltip config-secret"
              ></Tooltip>
              <span
                className="w-[200px] text-overflow ml-2 text-sm"
                title={item.name}
              >
                {item.name}
              </span>
              <span
                className="ml-5 flex-1 text-overflow text-[#757575] text-xs font-medium"
                title={item.description}
              >
                {item.description}
              </span>
              <img
                src={del}
                className="ml-6 w-4 h-4 cursor-pointer"
                onClick={() => deleteTool(item.toolId)}
                alt=""
              />
            </div>
          ))}
        </div>
      )}
      <div className="mt-[52px]">
        <div className="w-full font-medium text-second">
          <div
            className="flex items-center"
            style={{ marginBottom: '20px', justifyContent: 'space-between' }}
          >
            {multiModelDebugging && (
              <img
                src={growOrShrinkConfig?.knowledges ? arrowDown : arrowUp}
                className="w-[16px] h-[16px] mr-2 cursor-pointer"
                alt=""
                onClick={() =>
                  setGrowOrShrinkConfig({
                    ...growOrShrinkConfig,
                    knowledges: !growOrShrinkConfig.knowledges,
                  })
                }
              />
            )}
            <div style={{ display: 'flex' }}>
              <img src={settingFile} className="w-6 h-6" alt="" />
              <span className="text-[#13A10E] font-medium ml-2">
                {t('configBase.CapabilityDevelopment.knowledgeBase')}
              </span>
            </div>
            <div
              onClick={() => {
                setVisible(true);
              }}
              style={{ color: '#6356EA', cursor: 'pointer' }}
            >
              + {t('configBase.CapabilityDevelopment.addKnowledgeBase')}
            </div>
          </div>
          <Modal
            wrapClassName={styles.datasetModalWrap}
            open={visible}
            centered
            footer={null}
            closable={false}
            // width={461}
            forceRender
            maskClosable={false}
          >
            <div
              style={{ display: 'flex', justifyContent: ' space-between' }}
              className={styles.title}
            >
              <div>
                {t(
                  'configBase.CapabilityDevelopment.selectToAssociateTheDataset'
                )}
                <span
                  style={{ display: 'inline-block' }}
                  className={styles.refresh}
                  onClick={() => {
                    setIsFresh(true);
                    setTimeout(() => {
                      setIsFresh(false);
                    }, 500);
                    listRepos().then((res: any) => {
                      setDataSource(res?.pageData);
                    });
                  }}
                >
                  <img
                    src={
                      'https://aixfyun-cn-bj.xfyun.cn/bbs/88573.51517541305/%E5%88%B7%E6%96%B0.svg'
                    }
                    style={
                      isFresh
                        ? {
                            display: 'inline-block',
                            transform: 'rotate(360deg)',
                            transformOrigin: 'center',
                            transition: 'all 0.5s linear',
                          }
                        : {
                            display: 'inline-block',
                          }
                    }
                    alt=""
                  />
                  {t('configBase.CapabilityDevelopment.refresh')}
                </span>
              </div>
              <img
                alt=""
                className={styles.close}
                src={closeImg}
                onClick={() => setVisible(false)}
              />
            </div>
            <div
              style={{ position: 'relative' }}
              className={styles.data_content}
            >
              {dataSource?.length > 0 ? (
                (dataSource || []).map((item: any, index: number) => {
                  return (
                    <div
                      style={{
                        cursor:
                          disList.length == 0 || disList[0]?.tag == item.tag
                            ? 'pointer'
                            : 'not-allowed',
                      }}
                      key={item.id}
                      className={`${item.checked ? styles.checked : ''} ${
                        styles.cardlist
                      }`}
                      onClick={() => {
                        if (
                          disList.length == 0 ||
                          disList[0]?.tag == item.tag
                        ) {
                          item.checked = !item.checked;
                          setDataSource([...dataSource]);
                        }
                      }}
                    >
                      <div
                        style={{
                          position: 'absolute',
                          right: 0,
                          top: 0,
                          background:
                            item.tag == 'SparkDesk-RAG'
                              ? '#13A10e'
                              : item.tag == 'AIUI-RAG2'
                                ? 'linear-gradient(215deg, #6F8AF5 18%, #0458FF 82%)'
                                : 'linear-gradient(34deg, #6B23FF 19%, rgba(153, 98, 255, 0.9281) 83%)',
                          width: '58px',
                          height: '28px',
                          fontFamily: '苹方',
                          fontSize: '14px',
                          fontWeight: 500,
                          lineHeight: '28px',
                          letterSpacing: 'normal',
                          color: '#FFFFFF',
                          textAlign: 'center',
                          borderRadius: '0px 17px 0px 8px',
                        }}
                      >
                        {item.tag == 'SparkDesk-RAG'
                          ? t(
                              'configBase.CapabilityDevelopment.personalVersion'
                            )
                          : item.tag == 'AIUI-RAG2'
                            ? t('configBase.CapabilityDevelopment.stardust')
                            : t('configBase.CapabilityDevelopment.spark')}
                      </div>
                      <div className={styles.img}>
                        <img src={fileImg} alt="" />
                      </div>
                      <div className={styles.info}>
                        <div className={styles.name}>{item.name}</div>
                        <div className={styles.detail}>
                          <span title={item.charCount}>
                            {t('configBase.CapabilityDevelopment.character')}{' '}
                            {item.charCount ? item.charCount : 0}
                          </span>
                        </div>
                      </div>
                    </div>
                  );
                })
              ) : (
                <div className={styles.empty_card}>
                  <img
                    src="https://aixfyun-cn-bj.xfyun.cn/bbs/84929.66416893165/%E4%B8%8A%E4%BC%A0%E6%96%87%E4%BB%B6%E5%A4%87%E4%BB%BD%202.svg"
                    alt=""
                  />
                  <div className={styles.tips}>
                    {t(
                      'configBase.CapabilityDevelopment.youHaveNotCreatedAnyDatasets'
                    )}
                  </div>
                </div>
              )}
            </div>
            {dataSource?.length > 0 && (
              <div
                style={{ display: 'flex' }}
                className={styles.go_create}
                onClick={() => window.open('/resource/knowledge')}
              >
                <img
                  src="https://aixfyun-cn-bj.xfyun.cn/bbs/27965.529211835106/%E6%96%B0%E5%A2%9E.svg"
                  style={{ height: 12, marginRight: 2, marginTop: '3px' }}
                  alt=""
                />
                <div>
                  {t('configBase.CapabilityDevelopment.createNewDataset')}
                </div>
              </div>
            )}
            <div className={styles.button_list}>
              <Button
                onClick={() => {
                  setVisible(false);
                  (dataSource || []).forEach((item: any) => {
                    if (selectSource.includes(item)) {
                      item.checked = true;
                    } else {
                      item.checked = false;
                    }
                  });
                }}
              >
                {t('configBase.CapabilityDevelopment.cancel')}
              </Button>
              <Button
                type="primary"
                onClick={() => {
                  if (dataSource?.length > 0) {
                    setVisible(false);
                    const filterSource = (dataSource || []).filter(
                      (item: any) => item.checked
                    );
                    setSelectSource(filterSource);
                  } else window.open('/resource/knowledge');
                }}
              >
                {dataSource?.length > 0
                  ? t('configBase.CapabilityDevelopment.confirm')
                  : t('configBase.CapabilityDevelopment.goCreate')}
              </Button>
            </div>
          </Modal>
          {selectSource?.length > 0 && (
            <div className="flex items-center">
              <div className={styles.selectDataset}>
                {
                  <div className={styles.selectDatasetBox}>
                    <div
                      className={styles.selectDatasetBoxBtn}
                      onClick={() => {
                        setVisible(true);
                      }}
                    >
                      <img src="https://openres.xfyun.cn/xfyundoc/2024-01-22/47883fae-7d3e-46e2-bde0-e46b4753351b/1705888336589/addDatasetIcon.svg" />
                      {t('configBase.CapabilityDevelopment.addDataset')}
                    </div>
                    <div className={styles.datasetList}>
                      {(selectSource || []).map((item: any) => {
                        return (
                          <div key={item.id} className={styles.dataset}>
                            <div className={styles.datasetNameBox}>
                              <span className={styles.datasetName}>
                                <img src="https://openres.xfyun.cn/xfyundoc/2024-01-19/79de3a69-71e9-4e5a-b3cb-188df402f443/1705654589331/selectDatasetBtnIcon.svg" />
                                {item.name}
                              </span>
                              <img
                                onClick={() => {
                                  const filterSource = (
                                    selectSource || []
                                  ).filter((fs: any) => item.id !== fs.id);
                                  if (selectSource?.length == 1) {
                                    setDisList([]);
                                  }
                                  // 去掉chekced
                                  if (dataSource?.length > 0) {
                                    (dataSource || []).forEach((da: any) => {
                                      if (da.id === item.id) {
                                        da.checked = false;
                                      }
                                    });
                                    setSelectSource(filterSource);
                                  }
                                }}
                                src="https://openres.xfyun.cn/xfyundoc/2024-01-22/83a641b6-1132-4105-88f9-1d11b5f2d376/1705889402708/deleteDatasetIcon.svg"
                              />
                            </div>
                            <div className={styles.datasetInfo}>
                              {t('configBase.CapabilityDevelopment.character')}{' '}
                              {item.charCount ? item.charCount : 0}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  </div>
                }
              </div>
            </div>
          )}
        </div>
        {growOrShrinkConfig.knowledges && files.length > 0 && (
          <div className="mt-1.5 w-full overflow-auto max-h-[300px]">
            {files.map((item: any) => (
              <div
                key={item.id}
                className="flex items-center px-6 py-3 border-b border-[#E2E8FF]"
              >
                <img src={typeList.get(item.type)} className="w-5 h-5" alt="" />
                <span className="flex-1 text-overflow ml-2 text-sm">
                  {item.fullName}
                </span>
                <img
                  src={del}
                  className="ml-6 w-4 h-4 cursor-pointer"
                  onClick={() => deleteFile(item)}
                  alt=""
                />
              </div>
            ))}
          </div>
        )}
      </div>
      <div className="mt-[52px]">
        <div className="flex items-center">
          {multiModelDebugging && (
            <img
              src={growOrShrinkConfig?.chatStrong ? arrowDown : arrowUp}
              className="w-[16px] h-[16px] mr-2 cursor-pointer"
              alt=""
              onClick={() =>
                setGrowOrShrinkConfig({
                  ...growOrShrinkConfig,
                  chatStrong: !growOrShrinkConfig.chatStrong,
                })
              }
            />
          )}
          <img src={settingKaichangbai} className="w-6 h-6" alt="" />
          <span className="text-[#6407FD] font-medium ml-2">
            {t('configBase.CapabilityDevelopment.conversationEnhancement')}
          </span>
        </div>
        {growOrShrinkConfig.chatStrong && (
          <div className="flex flex-col gap-4 mt-5">
            <div
              className="border-b border-[#E9EFF6]"
              style={{
                padding: '8px 20px 12px 20px',
              }}
            >
              <div className="flex justify-between items-center">
                <div className="flex flex-col gap-2">
                  <span className="text-sm font-medium">
                    {t('configBase.CapabilityDevelopment.openingStatement')}
                  </span>
                </div>
                <Switch
                  className="list-switch config-switch"
                  checked={conversation}
                  onChange={checked => setConversation(checked)}
                />
              </div>
              {conversation && (
                <>
                  <div className="relative">
                    <div
                      className="absolute bottom-2 right-2.5 inline-flex items-center rounded-lg gap-1 cursor-pointer border border-[#6356EA] py-1 px-2.5 text-[#6356EA] text-sm bg-[#eff1f9] z-20"
                      onClick={() => setOpeningRemarksModal(true)}
                    >
                      <img src={aiGenerate} className="w-4 h-4" alt="" />
                      <span
                        onClick={() => {
                          if (!baseinfo.botName && !baseinfo.botDesc) {
                            return message.warning(
                              t(
                                'configBase.CapabilityDevelopment.pleaseFillInIntroductionAndName'
                              )
                            );
                          }
                          setShiliLoading(true);
                          generatePrologue({
                            name: baseinfo.botName,
                            botDesc: baseinfo.botDesc,
                          }).then(res => {
                            setPrologue(res);
                            setShiliLoading(false);
                          });
                          return;
                        }}
                      >
                        {t('configBase.CapabilityDevelopment.aiGenerated')}
                      </span>
                    </div>
                    <Spin
                      spinning={shiliLoading}
                      tip={t('configBase.CapabilityDevelopment.generating')}
                    >
                      <TextArea
                        className="mt-1.5 global-textarea pr-6"
                        placeholder={t(
                          'configBase.CapabilityDevelopment.pleaseEnterOpeningStatement'
                        )}
                        style={{ height: 96, resize: 'none' }}
                        value={prologue}
                        onChange={event => setPrologue(event.target.value)}
                      />
                    </Spin>
                  </div>
                </>
              )}
            </div>
            <div
              className="border-b border-[#E9EFF6]"
              style={{
                padding: '8px 20px 12px 20px',
              }}
            >
              <div className="flex justify-between items-center">
                <div className="flex  gap-2">
                  <div className="flex text-sm font-medium">
                    {t('configBase.CapabilityDevelopment.inputExample')}
                  </div>
                  {inputExampFlag && (
                    <div
                      onClick={
                        inputExampleLoading ? () => null : getInputExamples
                      }
                      className={cls(
                        styles.autoInputExampleBtn,
                        inputExampleLoading && styles.inputExampleLoading
                      )}
                      style={{ whiteSpace: 'nowrap', overflow: 'hidden' }}
                    >
                      <img
                        src="https://aixfyun-cn-bj.xfyun.cn/bbs/28921.014458559814/%E7%A7%91%E6%8A%80.svg"
                        alt=""
                      />
                      <span>
                        {t('configBase.CapabilityDevelopment.aiGenerated')}
                      </span>
                    </div>
                  )}
                  <p className={styles.threeLabelBox}>
                    <>
                      {inputExampleLoading && (
                        <img
                          className={styles.autoInputExamplesLoadingIcon}
                          src={autoInputExamplesLoadingIcon}
                        />
                      )}
                    </>
                  </p>
                </div>

                <Switch
                  className="list-switch config-switch"
                  checked={inputExampFlag}
                  onChange={checked => setInputExampFlag(checked)}
                />
              </div>
              {inputExampFlag && (
                <>
                  <div className={styles.inputExamples}>
                    <Input
                      className={styles.inputField}
                      maxLength={50}
                      placeholder={
                        placeholderText[botTypeValue]?.example1 ||
                        t(
                          'configBase.CapabilityDevelopment.femaleBabyWithSurnameZhang'
                        )
                      }
                      value={inputExample[0]}
                      onChange={(
                        event: React.ChangeEvent<HTMLInputElement>
                      ) => {
                        inputExample[0] = event.target.value;
                        setInputExample([...inputExample]);
                      }}
                    />
                    <Input
                      className={styles.inputField}
                      maxLength={50}
                      placeholder={
                        placeholderText[botTypeValue]?.example2 ||
                        t(
                          'configBase.CapabilityDevelopment.nameWithSurnameSong'
                        )
                      }
                      value={inputExample[1]}
                      onChange={(
                        event: React.ChangeEvent<HTMLInputElement>
                      ) => {
                        inputExample[1] = event.target.value;
                        setInputExample([...inputExample]);
                      }}
                    />
                    <Input
                      className={styles.inputField}
                      maxLength={50}
                      placeholder={
                        placeholderText[botTypeValue]?.example3 ||
                        t('configBase.CapabilityDevelopment.liNameWithSurname')
                      }
                      value={inputExample[2]}
                      onChange={(
                        event: React.ChangeEvent<HTMLInputElement>
                      ) => {
                        inputExample[2] = event.target.value;
                        setInputExample([...inputExample]);
                      }}
                    />
                  </div>
                </>
              )}
            </div>

            <Personality
              enablePersonality={personalityData.enablePersonality}
              personalityConfig={personalityData.personalityConfig}
              onPersonalityChange={setPersonalityData}
              botName={baseinfo.botName}
              botType={baseinfo.botType}
              botDesc={baseinfo.botDesc}
              prompt={prompt}
            />

            <div
              className="flex justify-between items-center border-b border-[#E9EFF6]"
              style={{
                padding: '8px 20px 12px 20px',
              }}
            >
              <div className="flex flex-col gap-2">
                <span className="text-sm font-medium">
                  {t('configBase.CapabilityDevelopment.roleSound')}
                </span>
              </div>
              <div
                style={{
                  display: 'flex',
                  borderRadius: '22px',
                  background: '#F2F5FE',
                  height: '44px',
                  justifyContent: 'center',
                  padding: '10px 16px',
                  cursor: 'pointer',
                }}
                className={`${styles.vcn_choose} ${styles.vcn_choose_banned}`}
                onClick={() => {
                  setShowSpeakerModal(true);
                }}
              >
                {renderBotVcn()}
              </div>
            </div>
            <div
              className="flex justify-between items-center border-b border-[#E9EFF6]"
              style={{
                padding: '8px 20px 12px 20px',
              }}
            >
              <div className="flex flex-col gap-2">
                <span className="text-sm font-medium">
                  {t(
                    'configBase.CapabilityDevelopment.supportMultiRoundConversation'
                  )}
                </span>
              </div>
              <Switch
                className="list-switch config-switch"
                checked={supportContextFlag}
                onChange={checked => setSupportContextFlag(checked)}
              />
            </div>

            <div className="border-b border-[#E9EFF6]">
              <div
                className="flex justify-between items-center"
                style={{
                  padding: '8px 20px 12px 20px',
                }}
              >
                <div className="flex">
                  <span className="text-sm font-medium">背景图</span>
                  <Tooltip
                    title="可以在对话后前往app查看实际竖屏效果"
                    overlayClassName="black-tooltip config-secret"
                  >
                    <QuestionCircleOutlined
                      style={{ marginLeft: '5px', cursor: 'pointer' }}
                    />
                  </Tooltip>
                </div>
                <Button
                  className={styles.uploadButton}
                  type="primary"
                  onClick={() => setUploadBackgroundModalVisible(true)}
                >
                  {backgroundImg ? '修改' : '上传'}
                </Button>
              </div>
              {backgroundImg && (
                <div className={styles.backgroundImgBox}>
                  <div className={styles.backgroundPc}>
                    <img
                      className={styles.backgroundImg}
                      src={backgroundImg}
                      alt=""
                    />
                    <div className={styles.hengping}>
                      <div className={styles.hengpingText}>横屏展示</div>
                      <div className={styles.shang}>
                        <div className={styles.left} />
                        <div className={styles.right} />
                      </div>
                      <div className={styles.zhong}>
                        <div className={styles.left} />
                        <div className={styles.right} />
                      </div>
                      <div className={styles.xia}>
                        <div className={styles.left} />
                        <div className={styles.right} />
                      </div>
                    </div>
                  </div>
                  <div className={styles.backgroundApp}>
                    <img
                      className={styles.backgroundImgApp}
                      src={backgroundImgApp}
                      alt=""
                    />
                    <div className={styles.shuping}>
                      <div className={styles.shupingText}>竖屏展示</div>
                      <div className={styles.shang}>
                        <div className={styles.left} />
                      </div>
                      <div className={styles.zhong}>
                        <div className={styles.left} />
                      </div>
                      <div className={styles.xia}>
                        <div className={styles.left} />
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
            <UploadBackgroundModal
              visible={uploadBackgroundModalVisible}
              onCancel={async () =>
                await setUploadBackgroundModalVisible(false)
              }
            />
          </div>
        )}
        <Checkbox
          style={{ marginTop: '20px' }}
          onChange={onChecked}
          checked={xieyi}
          className={styles.customCheckbox}
        >
          {t('configBase.CapabilityDevelopment.iHaveAgreed')}
          <a
            href="https://www.xfyun.cn/doc/policy/agreement.html"
            rel="noreferrer"
            target="_blank"
          >
            {t(
              'configBase.CapabilityDevelopment.xunfeiOpenPlatformServiceAgreement'
            )}
          </a>
          与
          <a
            href="https://www.xfyun.cn/doc/policy/privacy.html"
            rel="noreferrer"
            target="_blank"
          >
            {t('configBase.CapabilityDevelopment.privacyAgreement')}
          </a>
        </Checkbox>
      </div>
      <SpeakerModal
        vcnList={vcnList}
        changeSpeakerModal={setShowSpeakerModal}
        botCreateCallback={setBotCreateVcn}
        setBotCreateActiveV={setBotCreateActiveV}
        botCreateActiveV={botCreateActiveV}
        showSpeakerModal={showSpeakerModal}
      />
    </div>
  );
};

export default CapabilityDevelopment;
