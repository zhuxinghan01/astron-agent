import { useAntdTable } from "ahooks";
export interface Item {
  name: string;
  email: string;
  phone: string;
  gender: "male" | "female";
}

interface Result {
  total: number;
  list: Item[];
}

const getTableData = ({
  current,
  pageSize,
}: {
  current: number;
  pageSize: number;
}): Promise<Result> => {
  const query = `page=${current}&size=${pageSize}`;

  return fetch(`https://randomuser.me/api?results=55&${query}`)
    .then((res) => res.json())
    .then((res) => ({
      total: res.info.results,
      list: res.results,
    }));
};
export const useRpaDetail = () => {
  const { tableProps } = useAntdTable(getTableData);
  return {
    rpaDetail: {},
    tableProps,
  };
};
