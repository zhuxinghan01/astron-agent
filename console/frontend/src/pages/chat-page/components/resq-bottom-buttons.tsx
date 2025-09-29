import { MessageListType } from '@/types/chat';
import { ReactElement, useState } from 'react';
import { copyText } from '@/utils';
import copyIcon from '@/assets/imgs/chat/copy.svg';
import { ReactSVG } from 'react-svg';
import { Tooltip } from 'antd';
import AudioAnimate from './audio-animate';
import { useTranslation } from 'react-i18next';
import { getTtsSign } from '@/services/chat';
import TtsModule from './tts-module';

/**
 * 每个回复内容下面的按钮
 */
const ResqBottomButtons = ({
  message,
}: {
  message: MessageListType;
}): ReactElement => {
  const { t } = useTranslation();
  const [isPlaying, setIsPlaying] = useState<boolean>(false); // 是否正在播放音频

  // 播放语音
  const handlePlayAudio = () => {
    setIsPlaying(!isPlaying);
  };

  return (
    <div className="flex items-center ml-14 w-fit px-2 py-1 h-7">
      <TtsModule
        text={message.message}
        language="cn"
        isPlaying={isPlaying}
        setIsPlaying={setIsPlaying}
      />
      {/* <Tooltip
        title={
          isPlaying
            ? t('chatPage.chatBottom.stopReading')
            : t('chatPage.chatBottom.read')
        }
        placement="top"
      >
        <div
          onClick={() => handlePlayAudio()}
          className="text-sm cursor-pointer mr-3 copy-icon"
        >
          <AudioAnimate isPlaying={isPlaying} />
        </div>
      </Tooltip> */}
      <Tooltip title={t('chatPage.chatBottom.copy')} placement="top">
        <div
          onClick={() => copyText({ text: message.message })}
          className="text-sm cursor-pointer mr-3 copy-icon"
        >
          <ReactSVG wrapper="span" src={copyIcon} />
        </div>
      </Tooltip>
    </div>
  );
};

export default ResqBottomButtons;
