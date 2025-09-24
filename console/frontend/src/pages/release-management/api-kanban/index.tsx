import React, { useEffect, useState } from 'react';
import {  Select, Card } from 'antd';
import { useNavigate, useParams } from 'react-router-dom';
import { ExclamationCircleOutlined } from '@ant-design/icons';
import styles from './index.module.scss';
import arrowLeft from "@/assets/imgs/ApiKey/btn_zhishi_back.svg";
import titleRight from "@/assets/imgs/ApiKey/titleRight.png";
import keyIcon from "@/assets/imgs/ApiKey/keyIcon.png";
import equityIcon from "@/assets/imgs/ApiKey/equityIcon.png";
import timeIcon from "@/assets/imgs/ApiKey/timeIcon.png";
import formSelect from "@/assets/imgs/main/icon_nav_dropdown.svg";
import fileIcon from "@/assets/imgs/ApiKey/fileIcon.png";
import { getKeyDetail, getModelDetail, searchBotApiInfoByKeyId } from '@/services/apiKey';
import { getBotInfo } from '@/services/sparkCommon';
import dayjs from 'dayjs';
import { getBotInfoByBotId } from '@/services/agentSquare';
import { createChatList } from '@/api/chat';

interface keyInfoType {
  id: number;
  spaceId: number;
  createUid: number;
  name: string;
  description: string;
  appId: string;
  apiKey: string;
  apiSecret: string;
  deleted: number;
  createTime: string;
  updateTime: string;
  createName: string;
  avatar: string;
}

interface boundInfoType {
  botId: number;
  botName: string;
  appName: string;
  appId: string;
  apiKey: string;
  apiSecret: string;
  serviceUrl: string;
  documentUrl: string;
  flowId: string;
  keyId: number;
  keyName: string;
  count: number;
}
const APIDashboard: React.FC = () => {


  const navigate = useNavigate();
  const params = useParams();

  const [modelDetail, setModelDetail] = useState<any>({});
  const [modelList, setModelList] = useState<any>([]);
  const [boundInfo, setBoundInfo] = useState<boundInfoType | null>(null);
  const [botInfo, setBotInfo] = useState<any>(null);
  const [keyData, setKeyData] = useState<keyInfoType>({} as keyInfoType);

  const getKeyInfo = async () => {
    const res = await getModelDetail(params.id);
    setModelList(res)
    setModelDetail(res[0])
  }
  const getKeyListDetail = async () => {
    const res  = await getKeyDetail(params.id);
    setKeyData(res as unknown as keyInfoType);
  }
  const getBotApiInfo = async () => {
    const res: any = await searchBotApiInfoByKeyId(params.id);
    setBoundInfo(res)
    res && getBotDetail(res.botId);
  }
  const getBotDetail = async (id) => {
    const res = await getBotInfoByBotId(id);
    if (res) {
      setBotInfo(res);
    } else {
      await createChatList({ botId: id });
      const res = await getBotInfoByBotId(id);
      setBotInfo(res);
    }
  }
  useEffect(() => {
    getKeyInfo();
    getKeyListDetail()
    getBotApiInfo();
  }, []);
  const infoContainerItem: { id: number, title: string, key: string }[] = [
    {
      id: 1,
      title: '接口地址',
      key: 'serviceUrl',
    },
    {
      id: 2,
      title: 'API Secret',
      key: 'apiSecret',
    },
    {
      id: 3,
      title: 'API Key',
      key: 'apiKey',
    },
    {
      id: 4,
      title: 'API Flowid',
      key: 'flowId',
    },
  ]

  return (
    <div className={styles.keyInfoCardContainer}>
      <div className={styles.backButton}>
        <div
          className={styles.backButtonContainer}
          onClick={() => navigate(-1)}
        >
          <img src={arrowLeft} className={styles.backButtonIcon} alt="" />
          <span className={styles.backButtonText}>返回</span>
        </div>
      </div>
      {/* 顶部信息卡片 */}
      <div className={styles.keyInfoCard}>
        <div className={styles.keyInfoCardLeft}>
          <img src={keyIcon} className={styles.keyInfoCardAvatar} alt="" />
          <div className={styles.keyInfoCardContent}>
            <div className={styles.keyInfoCardContentLeft}>
              <div className={styles.keyInfoCardContentLeftTop}>
                {keyData.name}
              </div>
              <div className={styles.keyInfoCardContentLeftUser}>
                <img src={keyData.avatar} className={styles.userAvatar} alt="" />
                <span className={styles.userName}>
                  {keyData.createName}
                </span>
              </div>
            </div>
            {/* 线 */}
            <div className={styles.line} />
            <div className={styles.keyInfoCardContentRight}>
              <div className={styles.keyInfoCardContentRightTop}>
                描述说明：
              </div>
              <div className={styles.keyInfoCardContentRightDesc}>
                {keyData.description}
              </div>
            </div>

          </div>
        </div>
        <img src={titleRight} className={styles.keyInfoCardContentRightTitleImg} alt="" />

      </div>

      {
        boundInfo ? <div className={styles.boundInfoContainer}>
          <div className={styles.boundInfoHeader}>
            已绑定智能体
          </div>
          <div className={styles.boundInfoContent}>
            <div className={styles.boundInfoContentLeft}>
              <div className={styles.recommend_card_item}>
                <div className={`${styles.item_img}}`}>
                </div>
                <img
                  src={botInfo?.avatar}
                  alt=""
                  className={styles.avatar}
                />
                <div className={styles.bot_name}>{botInfo?.bot_name}</div>

                <div className={styles.bot_desc}>
                  {botInfo?.bot_desc}
                </div>

                <div className={styles.bot_author}>
                  <img
                    src={require("@/assets/imgs/home/author.svg")}
                    alt=""
                  />
                  <span>{botInfo?.creator_nickname || "@讯飞星火"}</span>
                  <img
                    src={require("@/assets/imgs/home/fire.svg")}
                    alt=""
                  />
                  <span>{botInfo?.hotNum}</span>
                </div>
              </div>
            </div>
            <div className={styles.boundInfoContentDesc}>
              <div className={styles.infoContainerTop}>
                <div className={styles.infoContainerTopItem}>
                  <img className={styles.infoContainerTopItemIcon} src={equityIcon} alt="" />
                  <span className={styles.infoContainerTopItemTitle}>使用权益额度</span>
                  <span className={styles.infoContainerTopItemNum}>{boundInfo.count || 0}</span>
                </div>
                <div className={styles.infoContainerTopLine} />
                <div className={styles.infoContainerTopItem}>
                  <img className={styles.infoContainerTopItemIcon} src={timeIcon} alt="" />
                  <span className={styles.infoContainerTopItemTitle}>权益到期时间</span>
                  <span className={styles.infoContainerTopItemNum}>{dayjs(modelDetail?.expireTime)?.format('YYYY-MM-DD')}</span>
                </div>
              </div>
              {/* 线 */}
              <div className={styles.infoContainerLine} />
              {
                infoContainerItem.map((item) => (
                  <div className={styles.infoContainerItem} key={item.id}>
                    <div className={styles.infoContainerTitle}>
                      {item.title}
                    </div>
                    <div className={styles.infoContainerDesc}>
                      {boundInfo[item.key] || '-'}
                    </div>
                  </div>
                ))
              }
            </div>
            <div className={styles.boundInfoContentRight}>
              <div className={styles.boundInfoContentRightTop}>
                <div className={styles.boundInfoContentRightTopTitle}>
                  模型名称
                </div>
                <Select
                  suffixIcon={<img src={formSelect} className="w-4 h-4 " />}
                  value={modelDetail?.modelName}
                  onChange={(value) => {
                    modelList.forEach((item) => {
                      if (item.modelName === value) {
                        setModelDetail(item);
                      }
                    })
                  }}
                  style={{ width: 287 }}
                >
                  {modelList.map((item, index) => (
                    <Select.Option key={index + item.modelName} value={item.modelName}>
                      {item.modelName}
                    </Select.Option>
                  ))}
                </Select>
              </div>
              <div className={styles.boundInfoContentRightDesc}>
                <div className={styles.tokenContainer}>
                  <div className={styles.tokenInfo}>
                    <div className={styles.tokenInfoTitle}>今日已用Tokens数</div>
                    <div className={styles.tokenInfoNum}>{modelDetail?.useCount || '_ _'}</div>
                  </div>
                  <div className={styles.line}></div>
                  <div className={styles.tokenInfo}>
                    <div className={styles.tokenInfoTitle}>剩余tokens数</div>
                    <div className={styles.tokenInfoNum}>{modelDetail?.leftCount || '_ _'}</div>
                  </div>
                </div>
                <div className={styles.line}></div>
                <div className={styles.qpsContainer}>
                  <div className={styles.qpsInfoTitle}>QPS</div>
                  <div className={styles.qpsInfoNum}>{modelDetail?.qpsCount || '_ _'}</div>
                </div>
              </div>
            </div>
          </div>

        </div> : <div className={styles.unboundTip}>
          <img src={fileIcon} className={styles.fileIcon} alt="" />
          暂未绑定智能体
        </div>

      }





    </div>
  );
};

export default APIDashboard;