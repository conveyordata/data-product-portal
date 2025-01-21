import { DataProductLifeCycleContract } from "./data-product-lifecycle.contract";

export type DataProductLifecycleCreateRequest = Pick<DataProductLifeCycleContract, 'name' | 'value' | 'is_default' | 'color'>;
export type DataProductLifecycleCreateResponse = DataProductLifeCycleContract;
