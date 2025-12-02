export interface DatasetCuratedQueryContract {
    output_port_id: string;
    sort_order: number;
    title: string;
    description?: string | null;
    query_text: string;
    created_at: string;
    updated_at?: string | null;
}

export interface DatasetCuratedQueriesContract {
    dataset_curated_queries: DatasetCuratedQueryContract[];
}
