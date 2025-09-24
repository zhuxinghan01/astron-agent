import { memo, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import back from "@/assets/imgs/common/back.png";
import { useNavigate } from "react-router-dom";
import { Table } from "antd";
import { ColumnsType } from "antd/es/table";
import { useRpaDetail } from "./hooks/use-rpa-detail";
import { ModalDetail } from "./components/modal-detail";
import useAntModal from "@/hooks/use-ant-modal";
import { RpaInfo, RpaRobot } from "@/types/rpa";
import dayjs from "dayjs";

export const RpaDetail = () => {
  const { rpaDetail } = useRpaDetail();
  const modalDetailRef = useRef<{ showModal: (values?: RpaRobot) => void }>(
    null
  );
  const columns: ColumnsType<RpaRobot> = [
    {
      title: "机器人名称",
      dataIndex: "name",
    },
    {
      title: "描述",
      dataIndex: "description",
    },
    {
      title: "参数",
      dataIndex: "parameters",
      width: 100,
      render: (_, record) => {
        return (
          <div
            className="text-[#275EFF] cursor-pointer"
            onClick={() => modalDetailRef.current?.showModal(record)}
          >
            详情
          </div>
        );
      },
    },
  ];
  return (
    <div className="w-full h-full  flex flex-col">
      <BackButton className="px-6" />
      <div className="flex flex-col mx-6 flex-1  my-[24px] bg-[#fff] rounded-2xl px-[24px] py-[24px]">
        <div className="w-full flex justify-between items-center">
          <div className="flex">
            <img className="w-[62px] h-[62px]" src="" alt="rpa" />
            <div className="pl-[24px]">
              <div className="text-2xl font-medium">
                {rpaDetail?.assistantName}
              </div>
              <div className="text-sm text-[#7F7F7F] pt-[12px]">
                {rpaDetail?.userName}
              </div>
            </div>
          </div>
          <div className="text-sm text-[#7F7F7F] pb-[16px]">
            更新于{dayjs(rpaDetail?.createTime).format("YYYY-MM-DD HH:mm:ss")}
          </div>
        </div>
        <div className="w-full text-[#7F7F7F]  pt-[12px] pb-[24px]">
          DeepSeek RPA 是由深度求索推出的推理大模型。Deepseek-R1
          在后训练阶段大规模使用了强化学习技术，在仅有极少标注数据的情况下，极大提升了模型推理能力。在致学、代码、自然语言推理等任务上，性能比肩
          OpenAl o1 正式版。
        </div>
        <div className="w-full pt-[32px] pb-[12px]">机器人资源列表</div>
        <div className="h-[400px]">
          <Table
            dataSource={rpaDetail?.robots}
            className="document-table"
            columns={columns}
            rowKey="project_id"
            style={{ overflow: "auto" }}
            pagination={false}
          ></Table>
        </div>
      </div>
      <ModalDetail ref={modalDetailRef} />
    </div>
  );
};

const BackButton: React.FC<{ className?: string }> = memo(({ className }) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const handleBack = (): void => navigate(-1);

  return (
    <button
      className={`flex items-center gap-2 mt-6 cursor-pointer hover:opacity-80 transition-opacity ${className}`}
      onClick={handleBack}
      type="button"
    >
      <img src={back} className="w-[18px] h-[18px]" alt="back" />
      <div className="mr-1 font-medium text-4">{t("rpa.back")}</div>
    </button>
  );
});

export default RpaDetail;
