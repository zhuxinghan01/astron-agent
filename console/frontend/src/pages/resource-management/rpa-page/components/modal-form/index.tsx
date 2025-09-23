import { CommonAntModalProps } from "@/hooks/use-ant-modal";
import { createRpa } from "@/services/rpa";
import { Button, Form, Input, message, Modal, Select, Space } from "antd";

export const ModalForm = ({
  commonAntModalProps,
}: {
  commonAntModalProps: CommonAntModalProps;
}) => {
  const [form] = Form.useForm();
  const handleSave = async () => {
    const values = await form.validateFields();
    createRpa(values)
      .then(() => {
        commonAntModalProps?.onCancel();
        message.success("创建成功");
      })
      .catch((error) => {
        commonAntModalProps?.onCancel();
        message.error(error.message);
      });
  };
  return (
    <Form form={form} layout="vertical" wrapperCol={{ span: 24 }}>
      <Modal {...commonAntModalProps} footer={null} title="创建 RPA">
        <div className="pt-[24px]">
          <Form.Item
            name="platform"
            label="RPA平台"
            required
            rules={[{ required: true, message: "请选择RPA平台" }]}
          >
            <Select
              placeholder="请选择RPA平台"
              options={[
                { label: "1", value: "1" },
                { label: "2", value: "2" },
                { label: "3", value: "3" },
              ]}
            />
          </Form.Item>
          <Form.Item
            name="accessKeyId"
            label="AccessKey ID"
            required
            rules={[{ required: true, message: "请输入AccessKey ID" }]}
          >
            <Input placeholder="请输入AccessKey ID" />
          </Form.Item>
          <Form.Item
            name="accessKey"
            label="AccessKey Secret"
            required
            rules={[{ required: true, message: "请输入AccessKey Secret" }]}
          >
            <Input placeholder="请输入AccessKey Secret" />
          </Form.Item>
          <div className="w-full flex justify-end">
            <Space>
              <Button onClick={() => commonAntModalProps?.onCancel()}>
                取消
              </Button>
              <Button type="primary" onClick={handleSave}>
                保存
              </Button>
            </Space>
          </div>
        </div>
      </Modal>
    </Form>
  );
};
