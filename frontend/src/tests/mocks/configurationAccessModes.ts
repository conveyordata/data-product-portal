import { HttpResponse, http } from 'msw';
import type { AccessModeWithType, GetAccessModes } from '@/store/api/services/generated/configurationAccessModesApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockAccessModes: AccessModeWithType[] = [
    {
        id: '1',
        name: 'Read Only',
        description: 'Read-only access to data',
        technical_asset_types: ['S3TechnicalAssetConfiguration'],
    },
    {
        id: '2',
        name: 'Read Write',
        description: 'Read and write access to data',
        technical_asset_types: ['S3TechnicalAssetConfiguration'],
    },
];

export const mockAccessModesHttp = (accessModes: AccessModeWithType[] = mockAccessModes) => {
    server.use(
        http.get('*/api/v2/configuration/access_modes', () => {
            return HttpResponse.json({ access_modes: accessModes } satisfies GetAccessModes);
        }),
    );
};
