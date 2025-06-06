import { ApiUrl } from '@/api/api-urls.ts';
import { baseApiSlice } from '@/store/features/api/base-api-slice.ts';
import { TagTypes } from '@/store/features/api/tag-types.ts';
import type { UserContract } from '@/types/users';

export const authTags: string[] = [TagTypes.Auth];

export const authApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: authTags }).injectEndpoints({
    endpoints: (builder) => ({
        authorize: builder.mutation<UserContract, void>({
            query: () => ({
                url: ApiUrl.Authorize,
                method: 'GET',
            }),
        }),
    }),
    overrideExisting: false,
});

export const { useAuthorizeMutation } = authApiSlice;
