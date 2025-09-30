import React, { useState, useRef, useEffect } from 'react';
import { message, Modal, Popover } from 'antd';
// import VoiceTraining from './voice-training'; // TODO: 确定是否使用
// import TrainingGuide from './training-guide';
import { useSparkCommonStore } from '@/store/spark-store/spark-common';
import { useLocaleStore } from '@/store/spark-store/locale-store';
import { vcnCnJson, vcnCnJsonEn, vcnEnJson, vcnOther } from './vcn';
import { localeConfig } from '@/locales/localeConfig';
import {
  getV2CustomVCNList,
  deleteCustomVCN,
  updateCustomVCN,
} from '@/services/spark-common';

import closeIcon from '@/assets/imgs/config-components/close-feedback.png';
import listenImg from '@/assets/svgs/listen_play.svg';
import listenStopImg from '@/assets/svgs/listen_stop.svg';

import styles from './index.module.scss';
import { ReactSVG } from 'react-svg';
import { useTranslation } from 'react-i18next';

interface SpeakerModalProps {
  changeSpeakerModal: any;
  botCreateMode?: boolean;
  botCreateCallback?: any;
  botCreateActiveV?: any;
  setBotCreateActiveV?: any;
}

const SpeakerModal: React.FC<SpeakerModalProps> = ({
  changeSpeakerModal,
  botCreateMode,
  botCreateCallback,
  botCreateActiveV,
  setBotCreateActiveV,
}) => {
  const activeV = useSparkCommonStore(state => state.activeVcn); // 选中的发音人
  const setActiveV = useSparkCommonStore(state => state.setActiveVcn);
  const { locale: localeNow } = useLocaleStore();
  const currentActiveV = botCreateMode ? botCreateActiveV : activeV;

  const { confirm } = Modal;
  const [vcnDisplay, setVcnDisplay] = useState<any[]>([]);
  const [playActive, setPlayActive]: any = useState(''); // 播放中的发音人
  const [showVoiceTraining, setShowVoiceTraining]: any = useState(false);
  const [showTrainingGuide, setShowTrainingGuide]: any = useState(false);
  const [showBGM, setShowBGM]: any = useState(true);
  const [mySpeaker, setMySpeaker]: any = useState([]); //我的发音人数组
  const [taskId, setTaskId]: any = useState(''); // 训练id
  const [editVCNId, setEditVCNId]: any = useState(''); // 编辑的训练id
  const [editVCNName, setEditVCNName]: any = useState(''); // 编辑的训练id
  const [audioInfo, setAudioInfo] = useState<any>({ assignVcn: '' });
  const [isAudioPlaying, setIsAudioPlaying] = useState<boolean>(false);
  const { t } = useTranslation();
  const audioRef: any = useRef(null);

  useEffect(() => {
    getMyVoicerList();
    if (localeNow === 'en') {
      setVcnDisplay(vcnCnJsonEn);
    } else {
      setVcnDisplay(vcnCnJson);
    }
  }, []);

  const setSpeaker = () => {
    message.success(localeConfig?.[localeNow]?.setSuccess);
    botCreateCallback && botCreateCallback(botCreateActiveV);
    changeSpeakerModal(false);
  };

  const getMyVoicerList = () => {
    getV2CustomVCNList()
      .then(res => {
        setMySpeaker(res);
      })
      .catch(err => {
        message.error(err.msg);
        console.log(err);
      });
  };

  const changeAudioBtn = (status: boolean) => {
    setIsAudioPlaying(false);
    setPlayActive('');
    console.log('playActive=>', '惊不惊喜，意不意外');
  };

  useEffect(() => {
    console.log('playActive=>', playActive);
  }, [playActive]);

  /**
   *
   * @param url
   * @param vcn
   * @param status
   * @returns
   */
  const audition = (url: string, vcn: string, status?: number) => {
    if (playActive === vcn) {
      //正在播放中，暂停当前的内容
      audioRef.current.pause();
      setIsAudioPlaying(false);
      setPlayActive('');
      return;
    }
    if (isAudioPlaying) {
      //先暂停
      setIsAudioPlaying(false);
      setPlayActive('');
    }
    if (status === 5) {
      //x5clone
      audioRef.current.pause(); //无论如何，先停掉
      setTimeout(() => {
        setAudioInfo({
          assignVcn: `x5_once_clone_${vcn}`,
        });
        setIsAudioPlaying(true);
      }, 100);
    } else {
      //
      audioRef.current.src = url;
      audioRef.current.play();
    }
    setTimeout(() => {
      setPlayActive(vcn);
    }, 100);
  };

  const deleteMySpeaker = (item: any) => {
    confirm({
      title: '删除发音人',
      content: '删除后，该发音人将无法使用，是否确认删除？',
      onOk() {
        deleteCustomVCN({ vcnId: item.vcnId })
          .then(res => {
            message.success('删除成功');
            getMyVoicerList();
          })
          .catch(err => {
            message.error(err.msg);
            console.log(err);
          });
      },
      onCancel() {
        console.log('Cancel');
      },
    });
  };

  const closeTrainModal = () => {
    setShowVoiceTraining(false);
    setIsAudioPlaying(false);
    getMyVoicerList();
  };

  const createMyVCN = () => {
    setShowTrainingGuide(false);
    getMyVoicerList();
    setShowVoiceTraining(true);
  };

  const continueRecord = (item: any) => {
    setTaskId(item.taskId);
    setShowVoiceTraining(true);
  };

  const editVCN = (e: any, item: any) => {
    e.stopPropagation();
    setEditVCNId(item.vcnId);
    setEditVCNName(item.name);
  };

  const updateVCNName = (e: { stopPropagation: () => void }, item: any) => {
    e.stopPropagation();
    const regex = /^[\u4e00-\u9fa5a-zA-Z0-9\s]+$/;
    if (!regex.test(editVCNName)) {
      message.info('发音人名称仅支持中英文、空格、数字');
      return;
    }
    updateCustomVCN({ vcnId: item.vcnId, name: editVCNName })
      .then(res => {
        message.success('修改成功');
        setEditVCNId('');
        getMyVoicerList();
      })
      .catch(err => {
        message.error(err.msg);
        console.log(err);
      });
  };

  // 关闭发音人时，播放暂停
  const closeSpeakerModal = () => {
    setIsAudioPlaying(false);
    setTimeout(() => {
      changeSpeakerModal(false);
    });
  };

  return (
    <div className={styles.speaker_modal}>
      <audio src="" ref={audioRef} onEnded={() => setPlayActive('')} />
      {/* {showVoiceTraining && (
        <VoiceTraining changeTrainModal={closeTrainModal} taskId={taskId} />
      )} */}
      {/* {showTrainingGuide && (
        <TrainingGuide
          changeTrainModal={() => {
            setShowTrainingGuide(false);
          }}
          onCreateVoice={createMyVCN}
        />
      )} */}
      {!showVoiceTraining && !showTrainingGuide && (
        <div className={styles.speaker_modal_content}>
          <div className={styles.modal_header}>
            {t('chooseVoice')}
            <img src={closeIcon} alt="" onClick={closeSpeakerModal} />
          </div>
          <div className={styles.speaker_type}>{t('Chinese')}</div>
          <div className={styles.speaker_container}>
            {vcnDisplay.map((item: any) => (
              <div
                className={`${styles.speaker_item} ${
                  currentActiveV?.cn === item.vcn ? styles.speaker_active : ''
                }`}
                key={item.vcn}
                onClick={() => {
                  if (!botCreateMode)
                    setActiveV({
                      ...activeV,
                      cn: item.vcn,
                      isDialect: item.isDialect || false,
                    });
                  else
                    setBotCreateActiveV({ ...botCreateActiveV, cn: item.vcn });
                }}
              >
                <div className={styles.vcn_info}>
                  <img
                    className={styles.speaker_img}
                    src={item.imgUrl}
                    alt=""
                  />
                  <span className={styles.vcn_name} title={item.name}>
                    {item.name}
                  </span>
                </div>
                <div
                  className={styles.try_listen}
                  onClick={(e: any) => {
                    e.stopPropagation();
                    audition(item.audioUrl, item.vcn);
                  }}
                  style={{ color: playActive === item?.vcn ? '#6178FF' : '' }}
                >
                  <img
                    src={playActive === item?.vcn ? listenStopImg : listenImg}
                    alt=""
                  />
                  {playActive === item?.vcn ? t('playing') : t('voiceTry')}
                </div>
              </div>
            ))}
          </div>
          <div className={styles.speaker_type}>{t('English')}</div>
          <div className={styles.speaker_container}>
            {vcnEnJson.map((item: any) => (
              <div
                key={item.vcn}
                className={`${styles.speaker_item} ${
                  currentActiveV?.en === item.vcn ? styles.speaker_active : ''
                }`}
                onClick={() => {
                  if (!botCreateMode) setActiveV({ ...activeV, en: item.vcn });
                  else
                    setBotCreateActiveV({ ...botCreateActiveV, en: item.vcn });
                }}
              >
                <div>
                  <img
                    className={styles.speaker_img}
                    src={item.imgUrl}
                    alt=""
                  />
                  {item.name}
                </div>
                <div
                  className={styles.try_listen}
                  onClick={(e: any) => {
                    e.stopPropagation();
                    audition(item.audioUrl, item.vcn);
                  }}
                  style={{ color: playActive === item?.vcn ? '#6178FF' : '' }}
                >
                  <img
                    src={playActive === item?.vcn ? listenStopImg : listenImg}
                    alt=""
                  />
                  {playActive === item?.vcn ? t('playing') : t('voiceTry')}
                </div>
              </div>
            ))}
          </div>

          <div className={styles.speaker_type}>
            {t('Multilingual')}
            <Popover
              color="#626366"
              overlayClassName="spearker-modal-type-tip-pop"
              title={null}
              content={t('MultilingualTip')}
            >
              <div className={styles.icon_wrap}>
                <ReactSVG
                  src="https://openres.xfyun.cn/xfyundoc/2024-07-10/e8398ed7-f019-419a-8004-41824306c41e/1720598757573/aaaaa.svg"
                  wrapper="span"
                />
              </div>
            </Popover>
          </div>

          <div className={styles.speaker_container}>
            {vcnOther.map((item: any) => (
              <div key={item.vcn} className={`${styles.speaker_item}`}>
                <div>
                  <img
                    className={styles.speaker_img}
                    src={item.imgUrl}
                    alt=""
                  />
                  {item.name}
                </div>
                <div
                  className={styles.try_listen}
                  onClick={(e: any) => {
                    e.stopPropagation();
                    audition(item.audioUrl, item.vcn);
                  }}
                  style={{ color: playActive === item?.vcn ? '#6178FF' : '' }}
                >
                  <img
                    src={playActive === item?.vcn ? listenStopImg : listenImg}
                    alt=""
                  />
                  {playActive === item?.vcn ? t('playing') : t('voiceTry')}
                </div>
              </div>
            ))}
          </div>
          <div className={styles.confirm_btn} onClick={() => setSpeaker()}>
            {t('btnOk')}
          </div>
        </div>
      )}
    </div>
  );
};

export default SpeakerModal;
