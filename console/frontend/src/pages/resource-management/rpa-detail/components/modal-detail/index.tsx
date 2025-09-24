import useAntModal from "@/hooks/use-ant-modal";
import { forwardRef, useImperativeHandle, useState } from "react";

import { Modal, Table } from "antd";
import { RpaParameter, RpaRobot } from "@/types/rpa";
import { ColumnsType } from "antd/es/table";

export const ModalDetail = forwardRef<{
  showModal: (values?: RpaRobot) => void;
}>((_, ref) => {
  const [currentRobot, setCurrentRobot] = useState<RpaRobot | null>(null);
  useImperativeHandle(ref, () => ({
    showModal: (values) => {
      setCurrentRobot(values || null);
      showModal();
    },
  }));
  const { commonAntModalProps, showModal } = useAntModal();
  const inColumns: ColumnsType<RpaParameter> = [
    {
      title: "参数名称",
      dataIndex: "varName",
      width: 160,
    },

    {
      title: "参数描述",
      dataIndex: "varDescribe",
    },
    // {
    //   title: "是否必填",
    //   dataIndex: "varDirection",
    //   width: 100,
    //   render: (_, record) => {
    //     return record.varDirection === 1 ? "是" : "否";
    //   },
    // },
    {
      title: "默认值",
      dataIndex: "varValue",
      width: 100,
    },
  ];
  const outColumns: ColumnsType<RpaParameter> = [
    {
      title: "参数名称",
      dataIndex: "varName",
    },
    {
      title: "参数描述",
      dataIndex: "varDescribe",
    },
    {
      title: "参数类型",
      dataIndex: "varType",
    },
  ];

  return (
    <Modal
      {...commonAntModalProps}
      footer={null}
      title={currentRobot?.name}
      maskClosable
    >
      <div className="pt-[24px]">
        <div className="pb-[20px]">输入参数</div>
        <Table
          dataSource={(currentRobot?.parameters || []).filter(
            (item) => item.varDirection === 0
          )}
          columns={inColumns}
          className="document-table"
          pagination={false}
        ></Table>
        <div className="py-[20px]">输出参数</div>
        <Table
          dataSource={(currentRobot?.parameters || []).filter(
            (item) => item.varDirection === 1
          )}
          columns={outColumns}
          className="document-table"
          pagination={false}
        ></Table>
      </div>
    </Modal>
  );
});
