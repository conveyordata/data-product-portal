import { createApi } from '@reduxjs/toolkit/query/react';

import { AppConfig } from '@/config/app-config.ts';
import { axiosBaseQuery } from '@/store/common/axios-base-query.ts';

// initialize an empty api service that we'll inject endpoints into later as needed
export const api = createApi({
    baseQuery: axiosBaseQuery({ baseUrl: AppConfig.getApiBaseURL() }),
    endpoints: () => ({}),
    reducerPath: 'generatedApi',
});
