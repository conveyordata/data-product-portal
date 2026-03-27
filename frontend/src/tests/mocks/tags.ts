import { HttpResponse, http } from 'msw';
import type { TagsGet, TagsGetItem } from '@/store/api/services/generated/configurationTagsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mock_tags: TagsGetItem[] = [
    {
        id: '1',
        value: 'tag1',
    },
];

export const mockGetTags = (tags: TagsGet = { tags: mock_tags }) => {
    server.use(
        http.get('*/api/v2/configuration/tags', () => {
            return HttpResponse.json(tags);
        }),
    );
};
