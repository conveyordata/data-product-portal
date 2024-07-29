import { DataOutputDatasetContract } from "../data-output-dataset";
import { DatasetContract } from "../dataset";

export type DataOutputDatasetLink = DataOutputDatasetContract & {
    dataset: DatasetContract;
};
