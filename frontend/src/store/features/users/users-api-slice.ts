import { ApiUrl } from '@/api/api-urls';
import { baseApiSlice } from '@/store/features/api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '@/store/features/api/tag-types';
import type { UserContract, UserCreateRequest } from '@/types/users';
import { UsersGetContract } from '@/types/users/user.contract';

export const userTags: string[] = [TagTypes.User];

export const usersApiSlice = baseApiSlice.enhanceEndpoints({ addTagTypes: userTags }).injectEndpoints({
    endpoints: (builder) => ({
        getAllUsers: builder.query<UsersGetContract, void>({
            query: () => ({
                url: ApiUrl.Users,
                method: 'GET',
            }),
            providesTags: (result = []) =>
                result
                    ? [
                          { type: TagTypes.User as const, id: STATIC_TAG_ID.LIST },
                          ...result.map(({ id }) => ({ type: TagTypes.User as const, id })),
                      ]
                    : [{ type: TagTypes.User, id: STATIC_TAG_ID.LIST }],
        }),
        createUser: builder.mutation<UserContract, UserCreateRequest>({
            query: (user) => ({
                url: ApiUrl.Users,
                method: 'POST',
                data: user,
            }),
            invalidatesTags: [{ type: TagTypes.User, id: STATIC_TAG_ID.LIST }],
        }),
    }),
    overrideExisting: false,
});

// Export hooks for usage in functional components, which are
// auto-generated based on the defined endpoints
export const { useGetAllUsersQuery, useCreateUserMutation } = usersApiSlice;
