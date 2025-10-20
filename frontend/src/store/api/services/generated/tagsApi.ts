import { api } from '@/store/api/services/generated/platformsApi';

const injectedRtkApi = api.injectEndpoints({
    endpoints: (build) => ({
        getTagsApiTagsGet: build.query<GetTagsApiTagsGetApiResponse, GetTagsApiTagsGetApiArg>({
            query: () => ({ url: '/api/tags' }),
        }),
        createTagApiTagsPost: build.mutation<CreateTagApiTagsPostApiResponse, CreateTagApiTagsPostApiArg>({
            query: (queryArg) => ({
                url: '/api/tags',
                method: 'POST',
                body: queryArg.tagCreate,
            }),
        }),
        updateTagApiTagsIdPut: build.mutation<UpdateTagApiTagsIdPutApiResponse, UpdateTagApiTagsIdPutApiArg>({
            query: (queryArg) => ({
                url: `/api/tags/${queryArg.id}`,
                method: 'PUT',
                body: queryArg.tagUpdate,
            }),
        }),
        removeTagApiTagsIdDelete: build.mutation<RemoveTagApiTagsIdDeleteApiResponse, RemoveTagApiTagsIdDeleteApiArg>({
            query: (queryArg) => ({
                url: `/api/tags/${queryArg.id}`,
                method: 'DELETE',
            }),
        }),
    }),
    overrideExisting: false,
});
export { injectedRtkApi as api };
export type GetTagsApiTagsGetApiResponse = /** status 200 Successful Response */ TagsGet[];
export type GetTagsApiTagsGetApiArg = void;
export type CreateTagApiTagsPostApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type CreateTagApiTagsPostApiArg = {
    tagCreate: TagCreate;
};
export type UpdateTagApiTagsIdPutApiResponse = /** status 200 Successful Response */ {
    [key: string]: string;
};
export type UpdateTagApiTagsIdPutApiArg = {
    id: string;
    tagUpdate: TagUpdate;
};
export type RemoveTagApiTagsIdDeleteApiResponse = /** status 200 Successful Response */ any;
export type RemoveTagApiTagsIdDeleteApiArg = {
    id: string;
};
export type TagsGet = {
    id: string;
    value: string;
};
export type ValidationError = {
    loc: (string | number)[];
    msg: string;
    type: string;
};
export type HttpValidationError = {
    detail?: ValidationError[];
};
export type TagCreate = {
    value: string;
};
export type TagUpdate = {
    value: string;
};
export const {
    useGetTagsApiTagsGetQuery,
    useLazyGetTagsApiTagsGetQuery,
    useCreateTagApiTagsPostMutation,
    useUpdateTagApiTagsIdPutMutation,
    useRemoveTagApiTagsIdDeleteMutation,
} = injectedRtkApi;
