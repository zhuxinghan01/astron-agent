import useChatStore from '@/store/chat-store';
import {
  type BotInfoType,
  type MessageListType,
  type UploadFileInfo,
  type SupportUploadConfig,
} from '@/types/chat';
import TextArea from 'antd/es/input/TextArea';
import { ReactElement, useCallback, useEffect, useRef, useState } from 'react';
import newChatIcon from '@/assets/imgs/chat/new-chat.svg';
import stopIcon from '@/assets/imgs/chat/stop-icon.svg';
import delIcon from '@/assets/imgs/chat/delete-history.svg';
import { useTranslation } from 'react-i18next';
import clsx from 'clsx';
import {
  clearChatList,
  postNewChat,
  getS3PresignUrl,
  uploadFileBindChat,
  unBindChatFile,
} from '@/services/chat';
import { message, Spin } from 'antd';
import { LoadingOutlined } from '@ant-design/icons';
import DeleteModal from './delete-modal';
import RecorderCom, { type RecorderRef } from './recorder-com';
import deleteIcon from '@/assets/imgs/chat/plugin/delete-file.png';
import { getFileIcon, getStatusText } from '@/utils';
import FilePreview from './file-preview';

const ChatInput = (props: {
  handleSendMessage: (params: {
    item: string;
    fileUrl?: string;
    callback?: () => void;
  }) => void;
  botInfo: BotInfoType;
  stopAnswer: () => void;
}): ReactElement => {
  const { handleSendMessage, botInfo, stopAnswer } = props;
  const { t } = useTranslation();
  const messageList = useChatStore(state => state.messageList); //  消息列表
  const streamId = useChatStore(state => state.streamId); //  流式id
  const isLoading = useChatStore(state => state.isLoading); //  是否正在加载
  const currentChatId = useChatStore(state => state.currentChatId); //  当前聊天id
  const addMessage = useChatStore(state => state.addMessage); //  添加消息
  const setMessageList = useChatStore(state => state.setMessageList); //  设置消息列表
  const setCurrentChatId = useChatStore(state => state.setCurrentChatId); //  设置当前聊天id
  const workflowOperation = useChatStore(state => state.workflowOperation); //  工作流操作
  const isWorkflowOption = useChatStore(state => state.isWorkflowOption); //  是否有工作流选项
  const chatFileListNoReq = useChatStore(state => state.chatFileListNoReq); //  文件列表
  const setChatFileListNoReq = useChatStore(
    state => state.setChatFileListNoReq
  ); //  设置文件列表
  const [deleteModalOpen, setDeleteModalOpen] = useState<boolean>(false); //  是否显示删除对话框
  const [isComposing, setIsComposing] = useState<boolean>(false); //  是否正在输入
  const [inputValue, setInputValue] = useState<string>(''); //  输入框值
  const textAreaRef = useRef<HTMLTextAreaElement>(null); //  输入框ref
  const $record = useRef<RecorderRef>(null); //  录音ref
  const [fileList, setFileList] = useState<UploadFileInfo[]>([]);
  const activeUploads = useRef(new Map()); // 存储正在上传的 XMLHttpRequest
  const activeBindings = useRef(new Map()); // 存储正在绑定的 AbortController
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [previewFile, setPreviewFile] = useState<UploadFileInfo>();

  // 检查是否有待选择的工作流选项
  const hasWorkflowOptionsToSelect = (): boolean => {
    if (!isWorkflowOption || !workflowOperation.length) return false;

    // 检查最后一条消息是否有未选择的选项
    const lastMessage = messageList[messageList.length - 1];
    if (
      lastMessage?.reqId === 'BOT' &&
      lastMessage?.workflowEventData?.option &&
      lastMessage.workflowEventData.option.length > 0
    ) {
      // 检查是否有选项没被选中
      const hasUnselectedOptions = lastMessage.workflowEventData.option.some(
        (option: any) => !option.selected
      );
      return hasUnselectedOptions;
    }
    return false;
  };

  useEffect(() => {
    setFileList(chatFileListNoReq);
  }, [chatFileListNoReq]);

  //全新对话
  const handleNewChat = async () => {
    if (streamId) {
      message.warning(t('chatPage.chatWindow.answeringInProgress'));
      return;
    }
    if (messageList.pop()?.reqId === 'START') {
      return;
    }
    try {
      await postNewChat(currentChatId);
      const startMessage: MessageListType = {
        id: new Date().getTime(),
        reqId: 'START',
        message: '全新的开始',
        updateTime: new Date().toISOString(),
      };
      addMessage(startMessage);
    } catch (error) {
      console.error('创建新对话失败:', error);
    }
  };

  //清除对话历史点击
  const handleClearChatList = () => {
    if (isLoading || streamId) {
      message.warning(t('chatPage.chatWindow.answeringInProgress'));
      return;
    }
    setDeleteModalOpen(true);
  };

  //清除对话历史确认
  const handleClearChatListConfirm = () => {
    clearChatList(currentChatId, botInfo.botId)
      .then(res => {
        setCurrentChatId(res.id);
        setMessageList([]);
        setDeleteModalOpen(false);
      })
      .catch(() => {
        message.error(t('chatPage.chatWindow.clearChatHistoryFailed'));
      });
  };

  //发送消息
  const handleSend = () => {
    if (!inputValue.trim()) {
      return;
    }

    // 检查是否有错误文件
    if (hasErrorFiles()) {
      message.error('请先删除上传失败的文件再发送消息');
      return;
    }

    handleSendMessage({
      item: inputValue,
      fileUrl: fileList[0]?.fileUrl,
      callback: () => {
        setInputValue('');
        setFileList([]);
      },
    });
  };

  //按下回车键
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSend();
    }
  };

  /**
   * 生成随机的文件业务Key
   */
  const generateFileBusinessKey = (): string => {
    return `${Date.now()}-${Math.random().toString(36).substring(2, 15)}`;
  };

  /**
   * 更新文件状态
   */
  const updateFileStatus = useCallback(
    (
      uid: string,
      fileId: string,
      status: 'pending' | 'uploading' | 'completed' | 'error',
      progress: number,
      fileUrl = '',
      error = ''
    ) => {
      setFileList(prev =>
        prev.map(file =>
          file.uid === uid
            ? { ...file, fileId, status, progress, fileUrl, error }
            : file
        )
      );
    },
    []
  );

  /**
   * 上传文件，并绑定到对话id上
   */
  const uploadFileToS3 = async (fileObj: UploadFileInfo) => {
    try {
      updateFileStatus(fileObj.uid, '', 'pending', 0, '', '');
      const signedRes = await getS3PresignUrl(fileObj.fileName, fileObj.type);
      const realFileUrl = signedRes.url.split('?')[0] || '';
      const arrayBuffer = await fileObj.file.arrayBuffer();
      updateFileStatus(fileObj.uid, '', 'uploading', 0, realFileUrl);

      return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        activeUploads.current.set(fileObj.uid, xhr);

        xhr.upload.addEventListener('progress', e => {
          if (e.lengthComputable) {
            const progress = Math.round((e.loaded / e.total) * 95);
            updateFileStatus(
              fileObj.uid,
              '',
              'uploading',
              progress,
              realFileUrl
            );
          }
        });

        xhr.addEventListener('load', async () => {
          activeUploads.current.delete(fileObj.uid);

          if (xhr.status >= 200 && xhr.status < 300) {
            // 创建可取消的绑定请求
            const bindController = new AbortController();
            activeBindings.current.set(fileObj.uid, bindController);

            try {
              const bindResult = await uploadFileBindChat(
                {
                  chatId: botInfo.chatId,
                  fileName: fileObj.fileName,
                  fileSize: fileObj.fileSize,
                  fileUrl: realFileUrl,
                  fileBusinessKey: fileObj.fileBusinessKey,
                },
                bindController.signal
              );

              // 绑定成功，清理控制器
              activeBindings.current.delete(fileObj.uid);

              updateFileStatus(
                fileObj.uid,
                bindResult,
                'completed',
                100,
                realFileUrl
              );
              resolve(true);
            } catch (error: any) {
              activeBindings.current.delete(fileObj.uid);

              if (error.name === 'AbortError') {
                // 请求被取消
                updateFileStatus(
                  fileObj.uid,
                  '',
                  'error',
                  0,
                  realFileUrl,
                  '绑定已取消'
                );
              } else {
                // 其他错误
                updateFileStatus(
                  fileObj.uid,
                  '',
                  'error',
                  0,
                  realFileUrl,
                  '绑定失败'
                );
              }
              reject(error);
            }
          } else {
            updateFileStatus(
              fileObj.uid,
              '',
              'error',
              0,
              realFileUrl,
              '上传失败'
            );
            reject(new Error('Upload failed'));
          }
        });

        xhr.addEventListener('error', () => {
          activeUploads.current.delete(fileObj.uid);
          updateFileStatus(
            fileObj.uid,
            '',
            'error',
            0,
            realFileUrl,
            '网络错误'
          );
          reject(new Error('Network error'));
        });

        xhr.addEventListener('abort', () => {
          activeUploads.current.delete(fileObj.uid);
        });

        xhr.open('PUT', signedRes.url);
        xhr.setRequestHeader(
          'Content-Type',
          fileObj.type || 'application/octet-stream'
        );
        xhr.send(arrayBuffer);
      });
    } catch (error) {
      activeUploads.current.delete(fileObj.uid);
      updateFileStatus(fileObj.uid, '', 'error', 0, '', '获取签名URL失败');
      throw error;
    }
  };

  /**
   * 开始上传文件
   */
  const handleStartUpload = async (files: UploadFileInfo[]) => {
    const pendingFiles = files.filter(file => file.status === 'pending');
    if (pendingFiles.length === 0) {
      return;
    }
    const uploadPromises = pendingFiles.map(file => uploadFileToS3(file));
    try {
      await Promise.allSettled(uploadPromises);
    } catch (error) {
      console.error('Upload error:', error);
    }
  };

  /**
   * 处理移除文件
   */
  const removeFile = (file: UploadFileInfo) => {
    if (file.fileId) {
      // 已绑定的文件，调用解绑接口
      unBindChatFile({
        chatId: botInfo.chatId,
        fileId: file.fileId,
      });
    } else {
      // 未绑定的文件，取消上传和绑定
      cancelUpload(file.uid);
      cancelBinding(file.uid);
    }
    setFileList(prev => prev.filter(f => f.uid !== file.uid));
  };

  /**
   * 取消上传
   */
  const cancelUpload = (uid: string) => {
    const xhr = activeUploads.current.get(uid);
    if (xhr) {
      xhr.abort();
      activeUploads.current.delete(uid);
      setFileList(prev =>
        prev.map(file =>
          file.uid === uid
            ? {
                ...file,
                status: 'pending' as const,
                progress: 0,
                error: '上传已取消',
              }
            : file
        )
      );
    }
  };

  /**
   * 取消绑定
   */
  const cancelBinding = (uid: string) => {
    const bindController = activeBindings.current.get(uid);
    if (bindController) {
      bindController.abort();
      activeBindings.current.delete(uid);
    }
  };

  /**
   * 检查是否有错误文件
   */
  const hasErrorFiles = (): boolean => {
    return fileList.some(file => file.status === 'error');
  };

  /**
   * 验证文件是否符合上传要求
   */
  const validateFile = (
    file: File,
    config: SupportUploadConfig
  ): string | null => {
    // 验证文件类型
    const acceptTypes = config.accept
      .toLowerCase()
      .split(',')
      .map(type => type.trim());
    const fileName = file.name.toLowerCase();
    const isValidType = acceptTypes.some(type => {
      if (type.startsWith('.')) {
        return fileName.endsWith(type);
      }
      return file.type.includes(type);
    });

    if (!isValidType) {
      return `${file.name}是不支持的文件类型`;
    }

    // 这里可以添加文件大小验证
    // const maxSize = 10 * 1024 * 1024; // 10MB
    // if (file.size > maxSize) {
    //   return '文件大小不能超过10MB';
    // }

    return null;
  };

  /**
   * 处理文件上传
   */
  const processSelectedFiles = async (files: File[]) => {
    // 检查数量限制
    if (
      fileList.length + files.length >
      (botInfo?.supportUploadConfig?.[0]?.limit || 0)
    ) {
      message.warning(
        `最多只能上传 ${botInfo?.supportUploadConfig?.[0]?.limit || 0} 个文件`
      );
      return;
    }
    // 验证成功的文件
    const validFiles: File[] = [];
    // 验证所有文件
    files.forEach(file => {
      const validationError = validateFile(
        file,
        botInfo?.supportUploadConfig?.[0] || ({} as SupportUploadConfig)
      );
      if (!validationError) {
        validFiles.push(file);
      }
    });

    if (validFiles.length > 0) {
      const newFiles = validFiles.map(file => ({
        uid: generateFileBusinessKey(),
        file,
        fileName: file.name,
        fileSize: file.size,
        type: file.type,
        status: 'pending' as const,
        fileUrl: '',
        fileBusinessKey: generateFileBusinessKey(),
        progress: 0,
        error: '',
      }));
      setFileList(prev => [...prev, ...newFiles]);
    }
  };

  /**
   * 处理文件选择
   */
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = Array.from(event.target.files || []);
    // 处理选择的文件
    processSelectedFiles(selectedFiles);
    // 清空input值，允许重复选择相同文件
    event.target.value = '';
  };

  /**
   * 触发文件选择
   */
  const triggerFileSelect = () => {
    fileInputRef.current?.click();
  };

  /**
   * 渲染单个文件项
   */
  const renderFileItem = (file: UploadFileInfo) => {
    const loading = !file.fileId && file.status !== 'error';
    return (
      <div
        key={file.uid}
        className="flex items-center justify-between p-2.5 mb-2 bg-gray-50 rounded-lg border border-gray-200 w-48"
        onClick={() => setPreviewFile(file)}
      >
        <div className="flex items-center flex-1 min-w-0">
          {/* 文件图标 */}
          <Spin
            spinning={loading}
            indicator={<LoadingOutlined spin />}
            size="small"
          >
            <img src={getFileIcon(file, loading)} alt="" className="w-6 h-8" />
          </Spin>

          {/* 文件信息 */}
          <div className="flex-1 ml-2 min-w-0">
            <div className="flex items-center justify-between">
              <span
                className="text-xs text-[#939393] truncate block max-w-[120px]"
                title={file.fileName}
              >
                {file.fileName}
              </span>
              {/* 操作按钮 */}
              <img
                src={deleteIcon}
                alt=""
                className="w-4 h-4 ml-2 flex-shrink-0 cursor-pointer hover:opacity-80"
                onClick={e => {
                  e.stopPropagation();
                  removeFile(file);
                }}
                title={file.fileId ? '删除文件' : '取消上传'}
              />
            </div>

            {/* 状态信息 */}
            <span
              className="text-xs truncate block max-w-full"
              style={{ color: file.status === 'error' ? '#ff4d4f' : '#939393' }}
            >
              {getStatusText(file)}
            </span>
          </div>
        </div>
      </div>
    );
  };

  // 自动开始上传
  useEffect(() => {
    handleStartUpload(fileList);
  }, [fileList.length]);

  // 同步到全局状态
  useEffect(() => {
    setChatFileListNoReq(fileList);
  }, [fileList]);

  return (
    <div className="pl-2.5 pr-[388px] py-6">
      <div className="w-full mx-auto max-w-[960px]">
        <div className="flex items-center relative">
          {messageList.length > 0 && (
            <div
              className="flex items-center justify-center w-auto h-8 px-2.5 border border-[#d3dbf8] rounded-2xl mb-3 cursor-pointer mr-3 bg-white text-[#333333] hover:border-[#5895f0]"
              onClick={handleNewChat}
            >
              <img src={newChatIcon} alt="" className="w-4 h-4" />
              <span className="text-sm  ml-2">
                {t('chatPage.chatWindow.newChat')}
              </span>
            </div>
          )}
          <div
            className="flex items-center justify-center w-auto h-8 px-2.5 border border-[#d3dbf8] rounded-2xl mb-3 cursor-pointer mr-3 bg-white text-[#333333] hover:border-[#5895f0]"
            onClick={handleClearChatList}
          >
            <img src={delIcon} alt="" className="w-3.5 h-3.5" />
            <span className="text-sm ml-2">
              {t('chatPage.chatWindow.clearChatHistory')}
            </span>
          </div>

          {streamId && (
            <div
              className="absolute right-2.5 flex items-center justify-center px-2 h-8 border border-[#d3dbf8] rounded-2xl mb-3 cursor-pointer bg-white text-[#333333] hover:border-[#5895f0]"
              onClick={stopAnswer}
            >
              <img src={stopIcon} alt="" className="w-4 h-4" />
              <span className="text-sm ml-2 ">
                {t('chatPage.chatWindow.stopOutput')}
              </span>
            </div>
          )}
        </div>
        <div
          className={clsx(
            'rounded-2xl min-h-[140px] bg-white border px-2.5 pt-4 border-[#d3dbf8] focus-within:border-[1.5px] focus-within:border-[#275eff]',
            {
              'opacity-50 cursor-not-allowed': hasWorkflowOptionsToSelect(),
            }
          )}
        >
          {/* 文件列表显示 */}
          {fileList.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {fileList.map(file => renderFileItem(file))}
            </div>
          )}
          <TextArea
            placeholder={
              hasWorkflowOptionsToSelect()
                ? t('chatPage.chatWindow.selectOptionFirst')
                : t('chatPage.chatWindow.defaultPlaceholder')
            }
            autoSize={{ minRows: 3, maxRows: 3 }}
            value={inputValue}
            onKeyDown={handleKeyDown}
            onChange={e => {
              setInputValue(e.target.value);
            }}
            className="chat-input-textarea"
            onCompositionStart={() => setIsComposing(true)}
            onCompositionEnd={() => setIsComposing(false)}
            ref={textAreaRef}
            readOnly={hasWorkflowOptionsToSelect()}
            disabled={hasWorkflowOptionsToSelect()}
          />
          <div className="flex items-center justify-between">
            {/* 文件上传区域 */}
            <div className="flex items-center">
              <input
                ref={fileInputRef}
                type="file"
                accept={botInfo?.supportUploadConfig?.[0]?.accept}
                multiple={(botInfo?.supportUploadConfig?.[0]?.limit || 0) > 1}
                onChange={handleFileSelect}
                style={{ display: 'none' }}
              />

              {/* 上传按钮 */}
              {botInfo?.supportUploadConfig?.length > 0 && (
                <div
                  className="flex items-center justify-center w-fit h-8 cursor-pointer transition-colors pl-2.5"
                  onClick={triggerFileSelect}
                  title={`上传${botInfo?.supportUploadConfig?.[0]?.type}文件 (${botInfo?.supportUploadConfig?.[0]?.accept})`}
                >
                  <img
                    src="https://openres.xfyun.cn/xfyundoc/2024-10-23/eb1e209f-e13f-4722-8561-8c564658e46d/1729648162929/adfsa.svg"
                    alt="上传文件"
                    className="w-3 h-3"
                  />
                  <span className="ml-2 text-sm text-gray-500">
                    {botInfo?.supportUploadConfig?.[0]?.tip}
                  </span>
                </div>
              )}
            </div>
            <div className="flex items-center pb-2.5">
              <RecorderCom
                ref={$record}
                disabled={hasWorkflowOptionsToSelect()}
                send={result => {
                  textAreaRef?.current?.focus();
                  setInputValue(prev => prev + result);
                }}
              />
              <div
                onClick={handleSend}
                className={clsx(
                  'w-10 h-10 bg-no-repeat bg-center ml-4 mr-1.5',
                  inputValue.trim() !== '' && !hasWorkflowOptionsToSelect()
                    ? "!bg-[url('@/assets/imgs/chat/send-hover.svg')] cursor-pointer"
                    : "bg-[url('@/assets/imgs/chat/send.svg')] cursor-not-allowed"
                )}
              />
            </div>
          </div>
        </div>
      </div>
      <DeleteModal
        open={deleteModalOpen}
        onCancel={() => setDeleteModalOpen(false)}
        onOk={handleClearChatListConfirm}
      />
      <FilePreview
        file={previewFile || ({} as UploadFileInfo)}
        onClose={() => setPreviewFile({} as UploadFileInfo)}
      />
    </div>
  );
};

export default ChatInput;
