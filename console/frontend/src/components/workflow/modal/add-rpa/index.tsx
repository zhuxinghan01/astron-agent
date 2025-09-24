import React, {
  useRef,
  useState,
  useMemo,
  useEffect,
  useCallback,
} from "react";
import { createPortal } from "react-dom";
import { Spin } from "antd";
import { getRpaList } from "@/services/rpa";
import { useMemoizedFn } from "ahooks";
import { throttle } from "lodash";
import dayjs from "dayjs";
import useFlowsManager from "@/components/workflow/store/useFlowsManager";
import { useTranslation } from "react-i18next";
import { useFlowCommon } from "@/components/workflow/hooks/useFlowCommon";
import { RpaListItem, RpaNode } from "@/components/workflow/types/modal";
import { Icons } from "@/components/workflow/icons";

import rpaIcon from "@/assets/imgs/common/icon_flow_item.png";
import publishIcon from "@/assets/imgs/workflow/publish-icon.png";
import knowledgeListEmpty from "@/assets/imgs/workflow/knowledge-list-empty.png";

export default function index(): React.ReactElement {
  const { handleAddRpaNode, resetBeforeAndWillNode } = useFlowCommon();
  const { t } = useTranslation();
  const getCurrentStore = useFlowsManager((state) => state.getCurrentStore);
  const currentStore = getCurrentStore();
  const currentFlow = useFlowsManager((state) => state.currentFlow);
  const willAddNode = useFlowsManager((state) => state.willAddNode);
  const nodes = currentStore((state) => state.nodes);
  const rpaModal = useFlowsManager((state) => state.rpaModalInfo.open);
  const setRpaModal = useFlowsManager((state) => state.setRpaModalInfo);
  const rpaRef = useRef<HTMLDivElement | null>(null);
  const [allData, setAllData] = useState<RpaListItem[]>([]);
  const [loading, setLoading] = useState<boolean>(false);

  const rpaList = useMemo((): Array<{ toolId?: string | undefined }> => {
    return nodes
      ?.filter((node: RpaNode) => node?.nodeType === "rpa-base")
      ?.map((node: RpaNode) => ({ toolId: node?.data?.nodeParam?.toolId }));
  }, [nodes]);

  const checkedIds = useMemo(() => {
    return rpaList?.map((item) => item?.toolId) || [];
  }, [rpaList]);

  useEffect(() => {
    if (rpaRef.current) {
      rpaRef.current.scrollTop = 0;
    }
    getRpas("");
  }, [currentFlow?.flowId]);

  function getRpas(value?: string): void {
    setLoading(true);
    getRpaList({
      name: value,
    })
      .then((data) => {
        setAllData(data);
      })
      .finally(() => setLoading(false));
  }

  const handleRpaChangeThrottle = useCallback(
    throttle((rpa) => {
      handleAddRpaNode(rpa);
    }, 1000),
    [nodes, willAddNode]
  );

  const handleCloseModal = useMemoizedFn(() => {
    setRpaModal({
      open: false,
    });
    resetBeforeAndWillNode();
  });

  return (
    <>
      {rpaModal
        ? createPortal(
            <div
              className="mask"
              style={{
                zIndex: 1001,
              }}
              onClick={(e) => e.stopPropagation()}
              onKeyDown={(e) => e.stopPropagation()}
            >
              <div className="p-6 pr-0 absolute bg-[#fff] rounded-2xl top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 text-second font-medium text-md w-[820px] h-[570px] flex flex-col">
                <div className="flex items-center justify-between font-medium pr-6">
                  <span className="font-semibold text-base">选择 RPA 工具</span>
                  <img
                    src={Icons.advancedConfig.close}
                    className="w-7 h-7 cursor-pointer"
                    alt=""
                    onClick={handleCloseModal}
                  />
                </div>
                <div
                  className="flex flex-col gap-2.5 mt-4 flex-1 pr-6"
                  style={{
                    overflow: "auto",
                  }}
                >
                  {loading ? (
                    <Spin />
                  ) : allData.length > 0 ? (
                    allData.map((item: RpaListItem) => {
                      return (
                        <div
                          key={item?.id}
                          className="flex flex-col bg-[#F7F7FA] p-4 rounded-lg gap-2"
                        >
                          <div className="flex items-center gap-2.5">
                            <div
                              className="w-7 h-7 flex items-center justify-center rounded-lg"
                              style={{
                                background: item.avatarColor
                                  ? item.avatarColor
                                  : item.address && item.icon
                                    ? `url(${item.address + item.icon}) no-repeat center / cover`
                                    : "#f0f0f0",
                              }}
                            >
                              {item.avatarColor &&
                                item.address &&
                                item.icon && (
                                  <img
                                    src={item.address + item.icon}
                                    className="w-[20px] h-[20px]"
                                    alt=""
                                  />
                                )}
                            </div>
                            <div className="flex items-center flex-1 overflow-hidden">
                              <p
                                className="flex-1 text-overflow text-sm font-medium"
                                title={item.name}
                              >
                                {item.name}
                              </p>
                            </div>
                            <div
                              className="flex items-center gap-1 cursor-pointer border border-[#E5E5E5] py-1 px-6 rounded-lg"
                              onClick={() => {
                                handleRpaChangeThrottle(item);
                              }}
                            >
                              <span>添加</span>
                              <span>
                                {checkedIds.filter(
                                  (toolId) => toolId === item.id
                                )?.length > 0
                                  ? checkedIds.filter(
                                      (toolId) => toolId === item.id
                                    )?.length
                                  : ""}
                              </span>
                            </div>
                          </div>
                          <div className="w-full flex items-start pl-[38px] gap-5 overflow-hidden">
                            <div className="flex items-center gap-1.5 flex-shrink-0">
                              <img
                                src={publishIcon}
                                className="w-3 h-3"
                                alt=""
                              />
                              <p className="text-[#757575] text-xs">
                                {`创建时间：${dayjs(item?.createTime)?.format(
                                  "YYYY-MM-DD HH:mm:ss"
                                )}`}
                              </p>
                            </div>
                            <div className="flex-1 flex items-center gap-1.5 flex-wrap">
                              {item?.inputs?.map((input) => (
                                <div
                                  key={input?.id}
                                  className="rounded-sm px-2 py-0.5 bg-[#fff] text-xs font-medium"
                                >
                                  {input?.name}
                                </div>
                              ))}
                            </div>
                          </div>
                          <div className="w-full flex items-start pl-[38px] gap-1 overflow-hidden">
                            <div className="text-[#757575] text-xs flex-shrink-0">
                              描述：
                            </div>
                            <div className="text-[#757575] text-xs text-overflow">
                              {item.description || "暂无描述"}
                            </div>
                          </div>
                        </div>
                      );
                    })
                  ) : (
                    <div className="mt-3 flex flex-col justify-center items-center gap-[30px] text-desc h-full">
                      <img
                        src={knowledgeListEmpty}
                        className="w-[124px] h-[122px]"
                        alt=""
                      />
                      <p>暂无RPA工具</p>
                    </div>
                  )}
                </div>
              </div>
            </div>,
            document.body
          )
        : null}
    </>
  );
}
