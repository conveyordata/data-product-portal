import userEvent from '@testing-library/user-event';
import { HttpResponse, http } from 'msw';
import { describe, expect, it } from 'vitest';
import { OutputPortForm } from '@/components/output-ports/output-port-form/output-port-form.component.tsx';
import {
    AbstractDataProductStatus,
    DataProductIconKey,
    DataProductVisibility,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockAccessDurationsGet, mockTimeBoundAccessEnabled } from '@/tests/mocks/configurationAccessDurations.ts';
import { mockDataProductLifecycles } from '@/tests/mocks/configurationDataProductLifecycles.ts';
import { mockOutputPortAccessTypes } from '@/tests/mocks/configurationOutputPortAccessTypes.ts';
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
    it('only allows Invite only access types for hidden data products', async () => {
        allowAllAuth();
        mockAccessDurationsGet();
        mockTimeBoundAccessEnabled();
        mockDataProductLifecycles();
        mockOutputPortAccessTypes();
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

        const select = await screen.findByRole('combobox', { name: /access type/i });
        expect(await screen.findByTitle('Private')).toBeInTheDocument();

        await userEvent.click(select);

        const option = (name: string) =>
            screen
                .getAllByText(name)
                .find((el) => el.closest('.ant-select-item-option'))
                ?.closest('.ant-select-item-option');
        expect(option('Unrestricted')).toHaveClass('ant-select-item-option-disabled');
        expect(option('Restricted')).toHaveClass('ant-select-item-option-disabled');
        expect(option('Private')).not.toHaveClass('ant-select-item-option-disabled');
        expect(screen.getByText('Hidden Data Products can only have hidden Output Ports')).toBeInTheDocument();
    });
});
