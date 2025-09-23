import { memo, useState } from "react";
import { useTranslation } from "react-i18next";
import back from "@/assets/imgs/common/back.png";
import { useNavigate } from "react-router-dom";
import { Table } from "antd";
import { ColumnsType } from "antd/es/table";
import { Item, useRpaDetail } from "./hooks/use-rpa-detail";
import { ModalDetail } from "./components/modal-detail";
import useAntModal from "@/hooks/use-ant-modal";

export const RpaDetail = () => {
  const { tableProps } = useRpaDetail();
  const { commonAntModalProps, showModal } = useAntModal();
  const [currentRecord, setCurrentRecord] = useState<Item | null>(null);
  const columns: ColumnsType<Item> = [
    {
      title: "机器人名称",
      dataIndex: "name",
    },
    {
      title: "描述",
      dataIndex: "email",
    },
    {
      title: "参数",
      dataIndex: "phone",
      width: 100,
      render: (_, record) => {
        return (
          <div
            className="text-[#275EFF] cursor-pointer"
            onClick={() => {
              setCurrentRecord(record);
              showModal();
            }}
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
              <div className="text-2xl font-medium">DeepSeek RPA</div>
              <div className="text-sm text-[#7F7F7F] pt-[12px]">
                用户名1122334
              </div>
            </div>
          </div>
          <div className="text-sm text-[#7F7F7F] pb-[16px]">
            更新于2025-02-09 18:08:52
          </div>
        </div>
        <div className="w-full text-[#7F7F7F]  pt-[12px] pb-[24px]">
          DeepSeek RPA 是由深度求索推出的推理大模型。Deepseek-R1
          在后训练阶段大规模使用了强化学习技术，在仅有极少标注数据的情况下，极大提升了模型推理能力。在致学、代码、自然语言推理等任务上，性能比肩
          OpenAl o1 正式版。
        </div>
        <div className="text-[#7F7F7F]">科大讯飞</div>
        <div className="w-full pt-[32px] pb-[12px]">机器人资源列表</div>
        <div className="h-[400px]">
          <Table
            className="document-table"
            {...tableProps}
            columns={columns}
            rowKey="id"
            style={{ overflow: "auto" }}
          ></Table>
        </div>
      </div>
      <ModalDetail
        commonAntModalProps={commonAntModalProps}
        title={currentRecord?.email}
      />
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
