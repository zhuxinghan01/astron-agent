import { memo } from "react";
import FixedOutputs from "../components/fixed-outputs";
import ExceptionHandling from "../components/exception-handling";
import SingleInput from "../components/single-input";

export const RpaDetail = memo((props: unknown) => {
  const { id, data } = props;
  console.log(id, data, 999996);

  return (
    <div className="p-[14px] pb-[6px]">
      <SingleInput id={id} data={data} />
      <FixedOutputs id={id} data={data} />
      <ExceptionHandling id={id} data={data} />
    </div>
  );
});
