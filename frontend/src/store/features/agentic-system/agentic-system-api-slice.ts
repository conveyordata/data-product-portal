import { AIApiUrl } from '@/api/api-urls';
import { HelloWorldContract } from '@/types/agentic-system';

import { baseAIApiSlice } from '../api/base-api-slice';
import { STATIC_TAG_ID, TagTypes } from '../api/tag-types';

export const agenticTags: string[] = [TagTypes.AI];

export const agenticSystemsApiSlice = baseAIApiSlice.enhanceEndpoints({ addTagTypes: agenticTags }).injectEndpoints({
    endpoints: (builder) => ({
        mainAIEndpoint: builder.query<HelloWorldContract, void>({
            query: () => ({
                url: AIApiUrl.HelloWorld,
                method: 'GET',
            }),
            providesTags: [{ type: TagTypes.AI as const, id: STATIC_TAG_ID.LIST }],
        }),
        askQuestion: builder.mutation<HelloWorldContract, string>({
            query: (question) => ({
                url: AIApiUrl.HelloWorld,
                method: 'POST',
                params: {
                    question: question,
                },
            }),
            // providesTags: [{ type: TagTypes.AI as const, id: STATIC_TAG_ID.LIST }],
        }),
    }),

    overrideExisting: false,
});

export const { useMainAIEndpointQuery, useAskQuestionMutation } = agenticSystemsApiSlice;
