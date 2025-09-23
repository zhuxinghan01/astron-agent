import React, { memo, FC } from "react";
import { useTranslation } from "react-i18next";

import { useNavigate } from "react-router-dom";
import RetractableInput from "@/components/ui/global/retract-table-input";
import { jumpTologin } from "@/utils/http";
import { useRpaPage } from "./hooks/use-rpa-page";
import { Button, Divider, Dropdown, Space } from "antd";
import { EllipsisOutlined } from "@ant-design/icons";
import { ToolItem } from "@/types/resource";
import useUserStore, { User } from "@/store/user-store";
import { ModalForm } from "./components/modal-form";
import useAntModal from "@/hooks/use-ant-modal";
const RpaPage: FC = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { rpas, isHovered, setIsHovered, handleSearchRpas } = useRpaPage();
  const user = useUserStore((state) => state.user);
  const { commonAntModalProps, showModal } = useAntModal();
  return (
    <div className="w-full h-full flex flex-col overflow-hidden py-8">
      <div
        className="flex justify-between mx-auto max-w-[1425px]"
        style={{
          width: "calc(0.85 * (100% - 8px))",
        }}
      >
        <div className="font-medium"></div>
        <RetractableInput
          restrictFirstChar={true}
          onChange={handleSearchRpas}
        />
      </div>
      <div className="w-full flex-1 overflow-scroll pt-6">
        <div
          className="h-full mx-auto max-w-[1425px]"
          style={{
            width: "85%",
          }}
        >
          <div className="grid lg:grid-cols-3 xl:grid-cols-3 2xl:grid-cols-3 3xl:grid-cols-3 gap-6">
            <div
              className={`rpa-card-add-container relative ${
                isHovered === null
                  ? ""
                  : isHovered
                    ? "rpa-no-hover"
                    : "rpa-hover"
              }`}
              onMouseLeave={(e) => {
                setIsHovered(true);
              }}
              onMouseEnter={(e) => {
                setIsHovered(false);
              }}
              onClick={() => {
                if (!user?.login && !user?.uid) {
                  return jumpTologin();
                }
                showModal?.();
              }}
            >
              <div className="color-mask"></div>
              <div className="rpa-card-add flex flex-col">
                <div className="flex justify-between w-full">
                  <span className="logo"></span>
                  <span className="add-icon"></span>
                </div>
                <div
                  className="mt-4 font-semibold add-name"
                  style={{ fontSize: 22 }}
                >
                  {t("rpa.createRpa")}
                </div>
              </div>
            </div>
            {rpas.map((rpa) => (
              <RpaCard rpa={rpa} key={rpa.id} user={user} />
            ))}
          </div>
        </div>
      </div>
      <ModalForm commonAntModalProps={commonAntModalProps} />
    </div>
  );
};

export const RpaCard = ({ rpa, user }: { rpa: ToolItem; user: User }) => {
  const navigate = useNavigate();
  const actions = new Map([
    [
      "edit",
      (record: any) => {
        // navigate(`/resource/rpa/create?id=${k.id}`);
      },
    ],
    [
      "delete",
      (record: any) => {
        // navigate(`/resource/rpa/create?id=${k.id}`);
      },
    ],
  ]);
  return (
    <div
      className="common-card-item rpa-card-item group"
      key={rpa.id}
      onClick={() => {
        if (rpa.status == 0) {
          if (!user?.login && !user?.uid) {
            return jumpTologin();
          }
          navigate(`/resource/rpa/create?id=${rpa.id}`);
        } else {
          navigate(`/resource/rpa/detail/${rpa.id}`);
        }
      }}
    >
      <div className="px-6">
        <div className="flex items-start gap-4">
          <span
            className="w-12 h-12 flex items-center justify-center rounded-lg"
            style={{
              background: rpa.avatarColor
                ? rpa.avatarColor
                : `url(${rpa.address + rpa.icon}) no-repeat center / cover`,
            }}
          >
            {rpa.avatarColor && (
              <img
                src={rpa.address + rpa.icon}
                className="w-[28px] h-[28px]"
                alt=""
              />
            )}
          </span>
          <div className="flex flex-col gap-2 flex-1 overflow-hidden">
            <div className="flex-1 flex items-center justify-between overflow-hidden">
              <span
                className="flex-1 text-overflow font-medium text-xl title-color title-size"
                title={rpa.name}
              >
                {rpa.name}
              </span>
            </div>
            <div
              className="text-desc text-overflow h-5 text-sm"
              title={rpa.description}
            >
              {rpa.description}11121
            </div>
          </div>
        </div>
      </div>
      <div className="text-sm px-6 pt-[6px] text-desc  text-overflow-more text-overflow-2">
        啊啊手机大叔啊啊手机大叔大婶都是啊啊手机大叔大婶都是啊啊手机大叔大婶都是大婶都是
      </div>
      <div
        className="flex justify-between items-center  overflow-hidden overflow-x-auto overflow-y-hidden py-[6px] px-6"
        style={{
          borderTop: "1px dashed #e2e8ff",
          scrollbarWidth: "none", // 隐藏滚动条
          msOverflowStyle: "none", // IE/Edge隐藏滚动条
        }}
      >
        <Space size={0} split={<Divider type="vertical" />}>
          <div className="text-desc">科大讯飞</div>
          <div className="text-desc">机器人资源：12个</div>
        </Space>
        <Dropdown
          menu={{
            onClick: ({ key, domEvent }) => {
              domEvent.stopPropagation();
              actions.get(key)?.(rpa);
            },
            items: [
              {
                label: <span className="text-[#275EFF]">编辑</span>,
                key: "edit",
              },
              {
                label: <span className="text-red-500">删除</span>,
                key: "delete",
              },
            ],
          }}
        >
          <EllipsisOutlined style={{ color: "#7F7F7F" }} />
        </Dropdown>
      </div>
    </div>
  );
};

export default memo(RpaPage);
