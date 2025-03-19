import { ApiUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import type { AccessRequest, AccessResponse } from '@/types/authorization';

const authorizationApiSlice = baseApiSlice.injectEndpoints({
    endpoints: (builder) => ({
        checkAccess: builder.query<AccessRequest, AccessResponse>({
            query: () => ({
                url: ApiUrl.AccessCheck,
                method: 'POST',
            }),
        }),
    }),
});

export const { useCheckAccessQuery } = authorizationApiSlice;
