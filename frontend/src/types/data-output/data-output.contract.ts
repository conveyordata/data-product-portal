import { DataOutputConfiguration } from ".";
import { DataProductContract } from "../data-product/data-product-contract";

export interface DataOutputContract {
    id: string;
    external_id: string;
    name: string;
    owner: DataProductContract;
    configuration: DataOutputConfiguration;
    configuration_type: string;
}

export interface DataOutputModel extends DataOutputContract {}
export type DataOutput = DataOutputContract
