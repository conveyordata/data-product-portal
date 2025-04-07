import { ApiUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import type { AccessRequest, AccessResponse } from '@/types/authorization';

const authorizationApiSlice = baseApiSlice.injectEndpoints({
    endpoints: (builder) => ({
        checkAccess: builder.query<AccessResponse, AccessRequest>({
            query: (access_request) => {
                // Log the full access_request object
                console.log('Access Request:', access_request);

                return {
                    url: ApiUrl.AccessCheck,
                    method: 'POST',
                    data: access_request,
                };
            },
        }),
    }),
});

export const { useCheckAccessQuery } = authorizationApiSlice;
