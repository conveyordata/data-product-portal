export type DatasetQueryStatsDailyResponse = {
    date: string;
    consumer_data_product_id: string;
    query_count: number;
    consumer_data_product_name: string | null;
};

export type DatasetQueryStatsDailyResponses = {
    dataset_query_stats_daily_responses: DatasetQueryStatsDailyResponse[];
};
