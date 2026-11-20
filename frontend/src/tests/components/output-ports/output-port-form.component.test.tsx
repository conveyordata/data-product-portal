import { HttpResponse, http } from 'msw';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import {
    AccessTypeSection,
    OutputPortForm,
} from '@/components/output-ports/output-port-form/output-port-form.component.tsx';
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
import { mockGroup, mockMachineUser } from '@/tests/mocks/identities.ts';
import {
    mockGetResourceNamesConstraints,
    mockResourceNamesSanitize,
    mockResourceNamesValidate,
} from '@/tests/mocks/resource_names.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockGetTags } from '@/tests/mocks/tags.ts';
import { mockUsers, mockUsersHttp } from '@/tests/mocks/users.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';
import { DecisionStatus, Prototype } from '@/types/roles';

describe('OutputPortForm', () => {
    beforeEach(() => {
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
    });

    it('only allows Invite only access types for hidden data products', async () => {
        const user = userEvent.setup();
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
            environments: [],
            tags: [],
            about: '',
            usage: null,
            domain: { id: 'domain-1', name: 'Sales', namespace: 'sales', description: 'Sales domain' },
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

        await user.click(select);

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

    it('only defaults user identities into user-only Output Port ownership', async () => {
        mockDataProductHttp();
        server.use(
            http.get('*/api/v2/authz/role_assignments/data_product', () =>
                HttpResponse.json({
                    role_assignments: [{ ...mockUsers[0], type: 'user' }, mockGroup, mockMachineUser].map(
                        (identity) => ({
                            identity,
                            role: { prototype: Prototype.OWNER },
                            decision: DecisionStatus.Approved,
                        }),
                    ),
                }),
            ),
        );
        renderWithProviders(<OutputPortForm mode="create" dataProductId="dp-1" />, { routerProps: {} });
        const owners = (await screen.findByLabelText('Owners')).closest('.ant-select');
        if (!owners) throw new Error('Owner field is missing');

        await waitFor(() =>
            expect(
                [...owners.querySelectorAll('.ant-select-selection-item')].map((item) => item.getAttribute('title')),
            ).toEqual(['Alice Smith (alice@example.com)']),
        );
    });

    it('does not change an existing access type while access types load', async () => {
        mockOutputPortAccessTypes();
        const onChange = vi.fn();

        renderWithProviders(<AccessTypeSection value="access-type-private" onChange={onChange} hiddenDataProduct />);

        expect(await screen.findByTitle('Private')).toBeInTheDocument();
        expect(onChange).not.toHaveBeenCalled();
    });
});
