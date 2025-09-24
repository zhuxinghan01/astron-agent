import {
  Button,
  Form,
  Input,
  Modal,
  Select,
  message,
  Row,
  Col,
  Checkbox,
} from 'antd';
import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { placeholderText } from '@/components/bot-center/edit-bot/placeholder';
import UploadCover from '@/components/upload-avatar/index';
import styles from './bot-info-modal.module.scss';
import closeIcon from '@/assets/images/create-bot-v2/close-icon.svg';
import {
  getBotType,
  submitBotBaseInfo,
  applyCancelUpload,
  sendApplyBot,
  uploadBotImg,
} from '@/services/sparkCommon';
import { useBotStateStore } from '@/store/spark-store/bot-state';
import Cropper from 'react-easy-crop';
import deleteBg from '@/assets/images/create-bot-v2/delete_bg.svg';

const BotInfoModal: React.FC<{
  show: boolean;
  onCancel: any;
  getBotBaseInfo: any;
  getBotChainInfo: any;
  setTongEditor?: any;
  qufabuFlag?: any;
  disjump?: any;
  setPageInfo?: any;
}> = ({
  show,
  onCancel,
  getBotBaseInfo,
  getBotChainInfo,
  setTongEditor,
  qufabuFlag,
  disjump,
  setPageInfo,
}) => {
  const [coverUrlPC, setCoverUrlPC] = useState('');
  const [coverUrlApp, setCoverUrlApp] = useState('');
  const [formData, setFormData] = useState<FormData>(); // blob 二进制文件流
  const [formDataPC, setFormDataPc] = useState<FormData>(); // blob 二进制文件流
  const [zoom, setZoom] = useState(1);
  const [zoomshu, setZoomshu] = useState(1);
  const [crop, setCrop] = useState({ x: 0, y: 0 });
  const [cropshu, setCropshu] = useState({ x: 0, y: 0 });
  const [file, setFile]: any = useState({});
  const [uploadedSrc, setUploadedSrc] = useState(''); // 这是本地选择的图像
  const inputRef = useRef<any>(null);
  const [checked, setChecked] = useState(true);
  const [form] = Form.useForm();
  const [botTypeList, setBotTypeList]: any = useState([]);
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [botTemplateInfoValue, _setBotTemplateInfoValue] = useState<any>(
    JSON.parse(sessionStorage.getItem('botTemplateInfoValue') ?? '{}')
  );
  const botBaseInfo = useBotStateStore((state) => state.botDetailInfo); // 助手详细信息
  const [editData, setEditData] = useState<any>({});
  const [pageOperate, setPageOperate] = useState<'create' | 'update'>('create'); // 页面操作模式()
  const [promptNow, setPromptNow] = useState();
  const [, setBotNameNow] = useState('');
  const [, setBotDescNow] = useState('');
  const name = Form.useWatch('name', form);
  const botDesc = Form.useWatch('botDesc', form);
  const botTypeValue = Form.useWatch('botType', form);
  const [inputExample, setInputExample] = useState<string[]>([]);
  const [coverUrl, setCoverUrl] = useState<string>(''); // 助手封面图
  const [isModalPeizhiUploadOpen, setIsModalPeizhiUploadOpen] = useState(false);

  useEffect(() => {
    if (uploadedSrc) {
      setIsModalPeizhiUploadOpen(true);
    }
  }, [uploadedSrc]);

  useEffect(() => {
    if (show) {
      getBotTypeList();
    }
  }, [show]);

  useEffect(() => {
    let op: any = searchParams.get('operate');
    if (['/botcenter/createbot'].includes(window.location.pathname)) {
      op = 'update';
    }
    setPageOperate(op);
    const botBaseInfoObj: any = { ...botBaseInfo };
    if (botBaseInfo?.botType == 0) {
      console.log(botBaseInfo);
      botBaseInfoObj.botType = null;
    }
    setEditData({
      ...botBaseInfoObj,
      name: botBaseInfo?.botName,
      type: 'update',
    });
    form.setFieldsValue({
      ...botBaseInfoObj,
      name: botBaseInfo?.botName,
      type: 'update',
    });
    setInputExample(botBaseInfo?.inputExample ?? []);
    setCoverUrl(botBaseInfo?.avatar);
    setCoverUrlApp(botBaseInfo?.appBackground);
    setCoverUrlPC(botBaseInfo?.pcBackground);
  }, [botBaseInfo]);

  const handlePeizhiUploadOk = () => {
    setIsModalPeizhiUploadOpen(false);
  };

  const handlePeizhiUploadCancel = () => {
    setUploadedSrc('');
    setIsModalPeizhiUploadOpen(false);
  };

  const handleDrop = (event: any) => {
    event.preventDefault();
    if (event.dataTransfer.items) {
      for (let i = 0; i < event.dataTransfer.items.length; i++) {
        if (event.dataTransfer.items[i].kind === 'file') {
          const file = event.dataTransfer.items[i].getAsFile();
          if (
            file.type !== 'image/png' &&
            file.type !== 'image/jpg' &&
            file.type !== 'image/jpeg'
          ) {
            message.warning('文件格式不支持');
            return;
          }
          setFile(file);
          const reader = new FileReader();
          reader.addEventListener('load', () => {
            setUploadedSrc(reader.result as string);
          });
          reader.readAsDataURL(file);
        }
      }
    } else {
      setFile(event.dataTransfer.files);
    }
  };

  const handleChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      const file: any = e.target.files[0];
      if (
        file.type !== 'image/png' &&
        file.type !== 'image/jpg' &&
        file.type !== 'image/jpeg'
      ) {
        message.warning('文件格式不支持');
        return;
      }
      if (file.type.startsWith('image/')) {
        if (file.size > 5 * 1024 * 1024) {
          message.error('文件大小不能超过5MB');
          return;
        }
        const reader = new FileReader();
        reader.addEventListener('load', () => {
          setUploadedSrc(reader.result as string);
        });
        reader.readAsDataURL(file);
      } else {
        message.error('只能上传图片');
      }
    }
  };

  /**
   * 获取助手类型list
   */
  const getBotTypeList = () => {
    getBotType()
      .then((data: any) => {
        setBotTypeList(data);
      })
      .catch((err) => {
        console.error(err);
        err?.msg && message.error(err.msg);
      });
  };

  /**
   * 校验
   */
  const validate = async () => {
    try {
      const values = await form.validateFields();
      if (!coverUrl) throw 'cover';
      return values;
    } catch (err) {
      console.log(err);
      message.warning('存在输入项未填写！');
      return false;
    }
  };

  /**
   * 点击取消按钮
   */
  const handleCancel = () => {
    if (editData?.type === 'create') {
      navigate('/botcenter/createbot');
    } else if (editData?.type === 'update') {
      onCancel();
    }
  };

  // 保存/更新助手基本信息
  const handleSave = async () => {
    const values = await validate();
    const botId = botBaseInfo?.botId;
    const operate = editData?.type;
    if (values) {
      const newBotInfo = {
        ...botBaseInfo,
        ...values,
        avatar: coverUrl,
        botId: botId || null,
        inputExample,
        appBackground: coverUrlApp,
        pcBackground: coverUrlPC,
      };
      if (Object.prototype.hasOwnProperty.call(newBotInfo, 'backgroundColor')) {
        delete newBotInfo.backgroundColor;
      }
      submitBotBaseInfo(newBotInfo)
        .then((res: any) => {
          const id = res?.botId || editData?.botId;
          if (operate === 'create') {
            searchParams.append('botId', id);
            searchParams.set('operate', 'update');
            setSearchParams(searchParams);
            message.success('创建成功！');
          }
          if (operate === 'update') message.success('更新成功！');
          getBotBaseInfo(id);
          getBotChainInfo(id);
          if (setTongEditor) {
            setTongEditor(newBotInfo);
          }

          onCancel();
        })
        .catch((e) => {
          message.error(e?.msg || '创建失败');
        });
    }
  };

  // 去发布
  const handleFabu = async () => {
    const values = await validate();
    const botId = botBaseInfo?.botId;
    const operate = editData?.type;
    if (values) {
      const newBotInfo = {
        ...botBaseInfo,
        ...values,
        avatar: coverUrl,
        botId: botId || null,
        inputExample,
        appBackground: coverUrlApp,
        pcBackground: coverUrlPC,
      };
      if (Object.prototype.hasOwnProperty.call(newBotInfo, 'backgroundColor')) {
        delete newBotInfo.backgroundColor;
      }
      await applyCancelUpload({ botId: botId, reason: '' });
      submitBotBaseInfo(newBotInfo)
        .then(async (res: any) => {
          const id = res?.botId || editData?.botId;
          if (operate === 'create') {
            searchParams.append('botId', id);
            searchParams.set('operate', 'update');
            setSearchParams(searchParams);
            message.success('创建成功！');
          }
          if (operate === 'update') message.success('更新成功！');
          getBotBaseInfo(id);
          getBotChainInfo(id);
          if (setTongEditor) {
            setTongEditor(newBotInfo);
          }
          setTimeout(() => {
            sendApplyBot({ botId: botId })
              .then(() => {
                onCancel();
                if (!disjump) {
                  navigate('/botcenter/createbot?sparkPlan=true', {
                    replace: true,
                  });
                }
                if (setPageInfo) {
                  setPageInfo((pre: any) => ({
                    ...pre,
                    pageIndex: 1,
                    botStatus: 1,
                  }));
                }
              })
              .catch((err) => {
                console.error(err);
                err?.msg && message.error(err.msg);
              });
          }, 400);
        })
        .catch((e) => {
          message.error(e?.msg || '创建失败');
        });
    }
  };

  /**
   * 输入示例
   * @param index 索引
   * @param value 值
   */
  const handleInputChange = (index: number, value: string) => {
    const updatedInputs = [...inputExample]; // 创建新数组以确保不可变性
    updatedInputs[index] = value; // 更新相应索引位置的值
    setInputExample(updatedInputs); // 更新状态
  };

  const onChecked = (e: any) => {
    setChecked(e.target.checked);
  };

  const onCropComplete = (_croppedArea: any, croppedAreaPixels: any) => {
    const image = new Image();
    image.src = uploadedSrc || '';
    image.onload = () => {
      // 确保图像已经加载
      const canvas = document.createElement('canvas');
      canvas.width = croppedAreaPixels.width;
      canvas.height = croppedAreaPixels.height;
      const ctx = canvas.getContext('2d');
      ctx &&
        ctx.drawImage(
          image,
          croppedAreaPixels.x * (image.width / image.naturalWidth),
          croppedAreaPixels.y * (image.height / image.naturalHeight),
          croppedAreaPixels.width * (image.width / image.naturalWidth),
          croppedAreaPixels.height * (image.height / image.naturalHeight),
          0,
          0,
          croppedAreaPixels.width,
          croppedAreaPixels.height
        );
      canvas.toBlob(
        (blob) => {
          const res = new FormData();
          blob && res.append('file', blob, 'cropped-image.jpeg');
          setFormDataPc(res);
        },
        'image/jpeg',
        1
      );
    };
  };
  const onCropCompleteshu = (_croppedArea: any, croppedAreaPixels: any) => {
    const image = new Image();
    image.src = uploadedSrc || '';
    image.onload = () => {
      // 确保图像已经加载
      const canvas = document.createElement('canvas');
      canvas.width = croppedAreaPixels.width;
      canvas.height = croppedAreaPixels.height;
      const ctx = canvas.getContext('2d');
      ctx &&
        ctx.drawImage(
          image,
          croppedAreaPixels.x * (image.width / image.naturalWidth),
          croppedAreaPixels.y * (image.height / image.naturalHeight),
          croppedAreaPixels.width * (image.width / image.naturalWidth),
          croppedAreaPixels.height * (image.height / image.naturalHeight),
          0,
          0,
          croppedAreaPixels.width,
          croppedAreaPixels.height
        );
      canvas.toBlob(
        (blob) => {
          const res = new FormData();
          blob && res.append('file', blob, 'cropped-image.jpeg');
          setFormData(res);
        },
        'image/jpeg',
        1
      );
    };
  };

  return (
    <div className={styles.bot_info_modal_wrap}>
      <Modal
        centered
        open={show}
        footer={null}
        maskClosable={false}
        width="575px"
        onCancel={handleCancel}
        getContainer={false}
        keyboard={false}
        closeIcon={<img src={closeIcon} alt="closeIcon" />}
      >
        <div className={styles.bot_info_modal}>
          <div className={styles.subtitle}>智能体基本信息</div>
          <Form
            form={form}
            name="botEdit"
            initialValues={{ ...editData }}
            onValuesChange={(_, value) => {
              if (value?.name && value?.name !== value?.name?.trim()) {
                form.setFields([{ name: 'name', value: value?.name?.trim() }]);
              }
              setPromptNow(value?.prompt ?? '');
              setBotNameNow(value?.name ?? '');
              setBotDescNow(value?.botDesc ?? '');
            }}
            onKeyDown={(e) => {
              e.stopPropagation();
              if (e.ctrlKey && e.key === 'v') {
                e.stopPropagation();
              }
            }}
          >
            <Row gutter={0}>
              <Col flex="auto">
                <Row gutter={0} style={{ marginBottom: '25px' }}>
                  <Col span={5}>
                    <Form.Item name="cover" required colon={false}>
                      <UploadCover
                        name={name}
                        botDesc={botDesc}
                        setCoverUrl={setCoverUrl}
                        coverUrl={coverUrl}
                      />
                    </Form.Item>
                  </Col>
                  <Col span={19}>
                    <Form.Item
                      label="智能体名称"
                      name="name"
                      rules={[{ required: true, message: '' }]}
                      colon={false}
                      labelCol={{ span: 24 }}
                      wrapperCol={{ span: 24 }}
                    >
                      <Input
                        maxLength={20}
                        placeholder={
                          placeholderText[botTypeValue]?.name || '起名大师'
                        }
                      />
                    </Form.Item>
                  </Col>
                </Row>
                <Form.Item
                  name="botType"
                  rules={[{ required: true, message: '' }]}
                  colon={false}
                  label="智能体类型"
                  labelCol={{ span: 24 }}
                >
                  <Select
                    placeholder="请选择智能体类型"
                    options={
                      botTypeList
                        ?.filter(
                          (item: any) => [0, 1, 2].indexOf(item?.key) === -1
                        )
                        ?.map((itm: any) => ({
                          label: itm?.name,
                          value: itm?.key,
                        })) ?? []
                    }
                  />
                </Form.Item>
                <Form.Item
                  label="智能体简介"
                  name="botDesc"
                  colon={false}
                  labelCol={{ span: 24 }}
                >
                  <Input.TextArea
                    showCount
                    maxLength={100}
                    placeholder={
                      placeholderText[botTypeValue]?.botDesc ||
                      '宝宝起名有困难？告诉我您的要求，我来给您出主意'
                    }
                    className={styles.textField}
                  />
                </Form.Item>
              </Col>
            </Row>
            <Form.Item
              label="开场白"
              name="prologue"
              colon={false}
              labelCol={{ span: 24 }}
            >
              <Input.TextArea
                showCount
                maxLength={200}
                placeholder={'你好~欢迎光临，有什么烦恼说来听听~'}
                className={styles.textField}
              />
            </Form.Item>
            <Form.Item
              label="示例"
              name="inputExample"
              colon={false}
              labelCol={{ span: 24 }}
            >
              <Row gutter={10}>
                <Col span={8}>
                  <Input
                    maxLength={50}
                    placeholder={
                      placeholderText[botTypeValue]?.example1 ||
                      '女宝宝，姓氏为张'
                    }
                    value={inputExample[0]}
                    onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                      handleInputChange(0, event.target.value.trim());
                    }}
                  />
                </Col>
                <Col span={8}>
                  <Input
                    maxLength={50}
                    placeholder={
                      placeholderText[botTypeValue]?.example2 ||
                      '姓宋，男宝宝，要求名字有平安、健康的寓意'
                    }
                    value={inputExample[1]}
                    onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                      handleInputChange(1, event.target.value.trim());
                    }}
                  />
                </Col>
                <Col span={8}>
                  <Input
                    maxLength={50}
                    placeholder={
                      placeholderText[botTypeValue]?.example3 || '姓李的女宝宝'
                    }
                    value={inputExample[2]}
                    onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
                      handleInputChange(2, event.target.value.trim());
                    }}
                  />
                </Col>
              </Row>
            </Form.Item>
            <div className={styles.prologue}>
              <div className={styles.titleBg}>
                <div>上传背景图</div>
                {coverUrlApp && (
                  <div>
                    <a
                      onClick={() => {
                        inputRef?.current?.click();
                      }}
                    >
                      重新上传
                    </a>
                    <span style={{ margin: '0px 6px' }}> | </span>
                    <img
                      style={{ cursor: 'pointer' }}
                      src={deleteBg}
                      onClick={() => {
                        setCoverUrlApp(''),
                          setCoverUrlPC(''),
                          setUploadedSrc('');
                      }}
                    />
                  </div>
                )}
              </div>
              <input
                accept="image/png,image/jpg,image/jpeg"
                ref={inputRef}
                style={{ display: 'none' }}
                type="file"
                multiple
                onChange={handleChange}
              />
              {!coverUrlPC && (
                <div
                  className={styles.shangchuangBg}
                  onClick={() => {
                    inputRef.current.value = '';
                    inputRef && inputRef?.current?.click();
                  }}
                  onDrop={handleDrop}
                  onDragOver={(e) => e.preventDefault()}
                />
              )}
              {coverUrlPC && (
                <div className={styles.huixianBg}>
                  <div className={styles.positionBox}>
                    <img
                      className={styles.coverUrlPC}
                      src={coverUrlPC}
                      alt=""
                    />
                    <div className={styles.hengTip}>横屏展示</div>
                  </div>
                  <div className={styles.positionBox}>
                    <img
                      className={styles.coverUrlApp}
                      src={coverUrlApp}
                      alt=""
                    />
                    <div className={styles.shuTip}>竖屏展示</div>
                  </div>
                </div>
              )}
            </div>
            {qufabuFlag && (
              <Checkbox
                onChange={onChecked}
                checked={checked}
                className={styles.customCheckbox}
              >
                我已同意
                <a
                  href="https://www.xfyun.cn/doc/policy/agreement.html"
                  rel="noreferrer"
                  target="_blank"
                >
                  讯飞开放平台服务协议
                </a>
                与
                <a
                  href="https://www.xfyun.cn/doc/policy/privacy.html"
                  rel="noreferrer"
                  target="_blank"
                >
                  隐私协议
                </a>
              </Checkbox>
            )}
            <div className={styles.bottom}>
              <Button onClick={handleCancel} className={styles.btn}>
                取消
              </Button>
              {!qufabuFlag && (
                <Button
                  className={styles.btn}
                  onClick={handleSave}
                  disabled={!checked}
                  type="primary"
                >
                  {editData?.type === 'create' && '创建'}
                  {editData?.type === 'update' && '更新'}
                </Button>
              )}
              {qufabuFlag && (
                <Button
                  className={styles.btn}
                  onClick={handleFabu}
                  disabled={!checked}
                  type="primary"
                >
                  去发布
                </Button>
              )}
            </div>
          </Form>
        </div>
      </Modal>
      <Modal
        centered
        zIndex={1001}
        wrapClassName={styles.peizhiUploadModel}
        footer={null}
        title="配置"
        open={isModalPeizhiUploadOpen}
        onOk={handlePeizhiUploadOk}
        onCancel={handlePeizhiUploadCancel}
      >
        <div>
          <div>上传背景图</div>
        </div>
        <div>
          {uploadedSrc && (
            <>
              <div className={styles.cropperBox}>
                <div
                  style={{
                    height: '195px',
                    width: '346px',
                    overflow: 'hidden',
                    position: 'relative',
                    marginRight: '15px',
                  }}
                >
                  <div className={styles.hengTip}>横屏展示</div>
                  <Cropper
                    image={uploadedSrc}
                    crop={crop}
                    zoom={zoom}
                    aspect={345 / 195} // 比例
                    onCropChange={setCrop}
                    onCropComplete={onCropComplete}
                    onZoomChange={setZoom}
                  />
                </div>
                <div className={styles.shupingHezi}>
                  <div className={styles.shuTip}>竖屏展示</div>
                  <Cropper
                    image={uploadedSrc}
                    crop={cropshu}
                    zoom={zoomshu}
                    aspect={145 / 195} // 比例
                    onCropChange={setCropshu}
                    onCropComplete={onCropCompleteshu}
                    onZoomChange={setZoomshu}
                  />
                </div>
              </div>
              <div className={styles.flexBoxTip}>
                <div className={styles.dian} />
                <div>拖动图片调整位置</div>
              </div>
            </>
          )}
        </div>
        <div>
          <div className={styles.peizhiBotton}>
            <div
              onClick={handlePeizhiUploadCancel}
              className={styles.peizhiCancel}
            >
              取消
            </div>
            <div
              className={
                uploadedSrc ? styles.peizhiQueren : styles.disabledButton
              }
              onClick={() => {
                if (!uploadedSrc) {
                  return;
                }
                uploadBotImg(formData as FormData).then((res) => {
                  setTimeout(() => {
                    uploadBotImg(formDataPC as FormData).then((resp) => {
                      setCoverUrlPC(resp);
                      setCoverUrlApp(res);
                      setIsModalPeizhiUploadOpen(false);
                    });
                  }, 500);
                });
              }}
            >
              确认
            </div>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default BotInfoModal;
