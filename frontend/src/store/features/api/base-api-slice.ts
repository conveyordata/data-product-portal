import { createApi } from '@reduxjs/toolkit/query/react';

import { AppConfig } from '@/config/app-config.ts';
import { axiosBaseQuery } from '@/store/features/api/axios-base-query.ts';

// initialize an empty api service that we'll inject endpoints into later as needed
export const baseApiSlice = createApi({
    baseQuery: axiosBaseQuery({ baseUrl: AppConfig.getApiBaseURL() }),
    endpoints: () => ({}),
});

export const baseAIApiSlice = createApi({
    baseQuery: axiosBaseQuery({ baseUrl: AppConfig.getAIApiBaseURL() }),
    endpoints: () => ({}),
    reducerPath: 'ai',
});
