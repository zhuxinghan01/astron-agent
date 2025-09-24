import { forwardRef, useImperativeHandle, useState } from "react";
import useAntModal, { CommonAntModalProps } from "@/hooks/use-ant-modal";
import { createRpa, getRpaSourceList, updateRpa } from "@/services/rpa";
import { RpaDetailFormInfo, RpaInfo } from "@/types/rpa";
import { useRequest } from "ahooks";
import { Button, Form, Input, message, Modal, Select, Space } from "antd";

export const ModalForm = forwardRef<
  { showModal: (values?: RpaDetailFormInfo) => void },
  {
    refresh: () => void;
  }
>(({ refresh }, ref) => {
  const [form] = Form.useForm();
  const [type, setType] = useState<"create" | "edit">("create");
  const { showModal, commonAntModalProps, open, closeModal } = useAntModal();
  const { data: rpaSourceList } = useRequest(
    open ? getRpaSourceList : () => [] as unknown as Promise<RpaInfo[]>,
    {
      refreshDeps: [open],
    }
  );
  useImperativeHandle(ref, () => ({
    showModal: (values) => {
      if (values) {
        form.setFieldsValue(values);
        setType("edit");
      } else {
        setType("create");
      }
      showModal();
    },
  }));
  const handleReset = () => {
    closeModal();
    form.resetFields();
  };
  const handleSave = async () => {
    const { platformId, assistantName, icon, id, ...values } =
      await form.validateFields();

    (type === "create"
      ? createRpa({ fields: values, platformId, assistantName, icon })
      : updateRpa(id, {
          fields: values,
          assistantName,
          icon,
          platformId,
        })
    )
      .then(() => {
        message.success(type === "create" ? "创建成功" : "编辑成功");
        refresh?.();
      })
      .catch((error) => {
        message.error(error.message);
      })
      .finally(() => {
        handleReset();
        refresh?.();
      });
  };

  return (
    <Form form={form} layout="vertical" wrapperCol={{ span: 24 }}>
      <Modal
        {...commonAntModalProps}
        footer={null}
        title={type === "create" ? "创建 RPA" : "编辑 RPA"}
        onCancel={handleReset}
      >
        <div className="pt-[24px]">
          <Form.Item name="id" label="id" hidden>
            <Input />
          </Form.Item>
          <Form.Item
            name="platformId"
            label="RPA平台"
            required
            rules={[{ required: true, message: "请选择RPA平台" }]}
          >
            <Select
              placeholder="请选择RPA平台"
              options={rpaSourceList?.map((item) => ({
                label: item.name,
                value: item.id,
              }))}
              onChange={(value) => {
                form.setFieldsValue({
                  assistantName: rpaSourceList?.find(
                    (item) => item.id === value
                  )?.name,
                  icon: rpaSourceList?.find((item) => item.id === value)?.icon,
                });
              }}
            />
          </Form.Item>
          <Form.Item name="assistantName" label="assistantName" hidden>
            <Input />
          </Form.Item>
          <Form.Item name="icon" label="icon" hidden>
            <Input />
          </Form.Item>
          <Form.Item dependencies={["platformId"]} noStyle>
            {({ getFieldValue }) => {
              const platformId = getFieldValue("platformId");
              const platformInfo = rpaSourceList?.find(
                (item) => item.id === platformId
              );
              const fields = JSON.parse(platformInfo?.value || "[]") as {
                key: string;
                name: string;
                required: boolean;
                desc: string;
              }[];

              return fields?.map((item) => {
                return (
                  <Form.Item
                    key={item.name}
                    name={item.name}
                    label={item.key}
                    required={item.required}
                  >
                    <Input placeholder={`请输入${item.desc}`} />
                  </Form.Item>
                );
              });
            }}
          </Form.Item>
          <div className="w-full flex justify-end">
            <Space>
              <Button onClick={() => handleReset()}>取消</Button>
              <Button type="primary" onClick={handleSave}>
                保存
              </Button>
            </Space>
          </div>
        </div>
      </Modal>
    </Form>
  );
});
