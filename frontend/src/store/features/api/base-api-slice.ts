import { createApi } from '@reduxjs/toolkit/query/react';
import { axiosBaseQuery } from '@/store/features/api/axios-base-query.ts';
import { AppConfig } from '@/config/app-config.ts';

// initialize an empty api service that we'll inject endpoints into later as needed
export const baseApiSlice = createApi({
    baseQuery: axiosBaseQuery({ baseUrl: AppConfig.getApiBaseURL() }),
    endpoints: () => ({}),
});
