import { HttpResponse, http } from 'msw';
import type { Environment } from '@/store/api/services/generated/configurationEnvironmentsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockEnvironments: Environment[] = [
    { id: 'env-dev', name: 'Development', acronym: 'dev', context: '', is_global: true },
    { id: 'env-prd', name: 'Production', acronym: 'prd', context: '', is_global: true },
    { id: 'env-tst', name: 'Test', acronym: 'tst', context: '', is_global: false },
];

export function mockGetEnvironments(environments = mockEnvironments) {
    server.use(http.get('*/api/v2/configuration/environments', () => HttpResponse.json({ environments })));
}
