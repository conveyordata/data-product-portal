import { ApiUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import type { AccessRequest, AccessResponse } from '@/types/authorization';

const authorizationApiSlice = baseApiSlice.injectEndpoints({
    endpoints: (builder) => ({
        checkAccess: builder.query<AccessResponse, AccessRequest>({
            query: (access_request) => ({
                url: ApiUrl.AccessCheck,
                method: 'POST',
                data: access_request,
            }),
        }),
    }),
});

export const { useCheckAccessQuery } = authorizationApiSlice;
