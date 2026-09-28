import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { OutputPortForm } from '@/components/output-ports/output-port-form/output-port-form.component.tsx';
import {
    AbstractDataProductStatus,
    DataProductIconKey,
    DataProductVisibility,
    OutputPortAccessType,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockAccessDurationsGet, mockTimeBoundAccessEnabled } from '@/tests/mocks/configurationAccessDurations.ts';
import { mockDataProductLifecycles } from '@/tests/mocks/configurationDataProductLifecycles.ts';
import { mockDataProductHttp } from '@/tests/mocks/dataProducts.ts';
import {
    mockGetResourceNamesConstraints,
    mockResourceNamesSanitize,
    mockResourceNamesValidate,
} from '@/tests/mocks/resource_names.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockGetTags } from '@/tests/mocks/tags.ts';
import { mockUsers, mockUsersHttp } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen } from '@/tests/test-utils.tsx';

describe('OutputPortForm', () => {
    it('only allows private access type for hidden data products', async () => {
        allowAllAuth();
        mockAccessDurationsGet();
        mockTimeBoundAccessEnabled();
        mockDataProductLifecycles();
        mockUsersHttp(mockUsers);
        mockGetTags();
        mockGetResourceNamesConstraints();
        mockResourceNamesSanitize();
        mockResourceNamesValidate();
        server.use(
            http.get('*/api/v2/authz/role_assignments/data_product/:dataProductId', () =>
                HttpResponse.json({ role_assignments: [] }),
            ),
        );
        mockDataProductHttp('dp-hidden', {
            id: 'dp-hidden',
            name: 'Hidden data product',
            description: 'Secret data product',
            namespace: 'hidden',
            status: AbstractDataProductStatus.Active,
            visibility: DataProductVisibility.Hidden,
            tags: [],
            about: '',
            usage: null,
            domain: { id: 'domain-1', name: 'Sales', description: 'Sales domain' },
            type: {
                id: 'type-1',
                name: 'Reporting',
                description: 'Reporting type',
                icon_key: DataProductIconKey.Reporting,
            },
            finalizers: [],
            lifecycle: { id: 'lc-1', name: 'Draft', value: 1, color: 'green', is_default: true },
        });

        renderWithProviders(<OutputPortForm mode="create" dataProductId="dp-hidden" />, {
            routerProps: { initialEntries: ['/'] },
        });

        const restricted = await screen.findByRole('radio', { name: 'Restricted' });
        const unrestricted = screen.getByRole('radio', { name: 'Unrestricted' });
        const privateOption = screen.getByRole('radio', { name: 'Private' });

        expect(restricted).toBeDisabled();
        expect(unrestricted).toBeDisabled();
        expect(privateOption).toHaveAttribute('value', OutputPortAccessType.Private);
    });
});
