export interface DatasetCuratedQueryContract {
    curated_query_id: string;
    output_port_id: string;
    title: string;
    description?: string | null;
    query_text: string;
    sort_order: number;
    created_at: string;
    updated_at?: string | null;
}

export interface DatasetCuratedQueriesContract {
    dataset_curated_queries: DatasetCuratedQueryContract[];
}
