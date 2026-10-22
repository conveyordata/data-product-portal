import { HttpResponse, http } from 'msw';
import {
    DomainStatus,
    type GetDomainsApiResponse,
    type GetDomainsItem,
} from '@/store/api/services/generated/configurationDomainsApi.ts';
import { server } from '@/tests/mocks/server.ts';
export const mock_domains: GetDomainsItem[] = [
    {
        id: 'id-1',
        name: 'Finance',
        namespace: 'finance',
        description: 'My beautiful domain',
        status: DomainStatus.Active,
        finalizers: [],
        abstract_data_product_count: 31,
    },
];
export const mockGetDomains = (domains: GetDomainsItem[] = mock_domains) => {
    server.use(
        http.get('*/api/v2/configuration/domains', () => {
            return HttpResponse.json({ domains: domains } as GetDomainsApiResponse);
        }),
    );
};
