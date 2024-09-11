import { DataOutputTechnicalInfo } from "@/components/data-outputs/data-output-technical-info/data-output-technical-info.component";

type Props = {
    dataOutputId: string;
};

export function TechnologiesTab({ dataOutputId }: Props) {
    return <>
    <DataOutputTechnicalInfo data_output_id={dataOutputId}/>
    </>
}
