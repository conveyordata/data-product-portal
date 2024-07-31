import { DataOutputConfiguration } from ".";
import { DataProductContract } from "../data-product/data-product-contract";
import { DataOutputDatasetLink } from "./dataset-link.contract";

export interface DataOutputContract {
    id: string;
    external_id: string;
    description: string;
    name: string;
    owner: DataProductContract;
    owner_id: string;
    configuration: DataOutputConfiguration;
    configuration_type: string;
    dataset_links: DataOutputDatasetLink[];
}

export interface DataOutputModel extends DataOutputContract {}
//export type DataOutput = DataOutputContract
