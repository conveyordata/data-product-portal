export interface DataProductLifeCycleContract {
    id: string;
    value: number;
    name: string;
    color: string;
    is_default: boolean;
}

export interface DataProductLifecycleModel extends DataProductLifeCycleContract {}
