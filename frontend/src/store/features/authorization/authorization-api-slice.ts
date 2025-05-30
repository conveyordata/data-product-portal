import { ApiUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import type { AccessRequest, AccessResponse } from '@/types/authorization';

const authorizationApiSlice = baseApiSlice.injectEndpoints({
    endpoints: (builder) => ({
        checkAccess: builder.query<AccessResponse, AccessRequest>({
            query: (access_request) => {
                const searchParams = new URLSearchParams();

                if (access_request.domain) searchParams.append('domain', access_request.domain);
                if (access_request.resource) searchParams.append('resource', access_request.resource);

                return {
                    url: `${ApiUrl.AccessCheck}/${access_request.action}?${searchParams.toString()}`,
                    method: 'GET',
                };
            },
        }),
        isAdmin: builder.query<boolean, void>({
            query: () => ({
                url: ApiUrl.AdminCheck,
                method: 'GET',
            }),
        }),
    }),
});

export const { useCheckAccessQuery, useIsAdminQuery } = authorizationApiSlice;
