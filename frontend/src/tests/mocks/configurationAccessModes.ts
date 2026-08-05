import { HttpResponse, http } from 'msw';
import type { AccessMode, GetAccessModes } from '@/store/api/services/generated/configurationAccessModesApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockAccessModes: AccessMode[] = [
    {
        id: '1',
        name: 'Read Only',
        description: 'Read-only access to data',
    },
    {
        id: '2',
        name: 'Read Write',
        description: 'Read and write access to data',
    },
];

export const mockAccessModesHttp = (accessModes: AccessMode[] = mockAccessModes) => {
    server.use(
        http.get('*/api/v2/configuration/access_modes', () => {
            return HttpResponse.json({ access_modes: accessModes } satisfies GetAccessModes);
        }),
    );
};
