import { CommonAntModalProps } from "@/hooks/use-ant-modal";

import { Modal, Table } from "antd";

export const ModalDetail = ({
  commonAntModalProps,
  title,
}: {
  commonAntModalProps: CommonAntModalProps;
  title?: string;
}) => {
  const inColumns = [
    {
      title: "参数名称",
      dataIndex: "name",
      width: 160,
    },

    {
      title: "参数描述",
      dataIndex: "type",
    },
    {
      title: "是否必填",
      dataIndex: "required",
      width: 100,
    },
    {
      title: "默认值",
      dataIndex: "default",
      width: 100,
    },
  ];
  const outColumns = [
    {
      title: "参数名称",
      dataIndex: "name",
    },
    {
      title: "参数描述",
      dataIndex: "description",
    },
    {
      title: "参数类型",
      dataIndex: "type",
    },
  ];

  return (
    <Modal {...commonAntModalProps} footer={null} title={title} maskClosable>
      <div className="pt-[24px]">
        <div className="pb-[20px]">输入参数</div>
        <Table
          dataSource={[]}
          columns={inColumns}
          className="document-table"
        ></Table>
        <div className="pb-[20px]">输出参数</div>
        <Table
          dataSource={[]}
          columns={outColumns}
          className="document-table"
        ></Table>
      </div>
    </Modal>
  );
};
