import { listRpas } from "@/services/rpa";
import globalStore from "@/store/global-store";
import useUserStore, { User } from "@/store/user-store";
import { ToolItem } from "@/types/resource";
import { useRequest, useDebounceFn } from "ahooks";
import React, { useCallback, useEffect, useState } from "react";

export const useRpaPage = (): {
  handleSearchRpas: (e: React.ChangeEvent<HTMLInputElement>) => void;
  isHovered: boolean | null;
  setIsHovered: React.Dispatch<React.SetStateAction<boolean | null>>;
  rpas: ToolItem[];
} => {
  const [isHovered, setIsHovered] = useState<boolean | null>(null);
  const [searchValue, setSearchValue] = useState("");

  const { data } = useRequest(
    () =>
      listRpas({
        content: searchValue?.trim(),
        pageNo: 1,
        pageSize: 20,
      }),
    {
      refreshDeps: [searchValue],
    }
  );

  const { run: handleSearchRpas } = useDebounceFn(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      setSearchValue(value);
    },
    { wait: 500 }
  );

  return {
    handleSearchRpas,
    isHovered,
    setIsHovered,
    rpas: data?.pageData || [],
  };
};
