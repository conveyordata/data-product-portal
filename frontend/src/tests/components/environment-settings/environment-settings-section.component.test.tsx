import { HttpResponse, http } from 'msw';
import type { ComponentProps } from 'react';
import { describe, expect, it } from 'vitest';
import { EnvironmentSettingsSection } from '@/components/environment-settings/environment-settings-section.component.tsx';
import { UIElementType } from '@/store/api/services/generated/pluginsApi.ts';
import { mockEnvironments } from '@/tests/mocks/configurationEnvironments.ts';
import { server } from '@/tests/mocks/server.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const sizeField = {
    name: 'size',
    label: 'Size',
    type: UIElementType.Select,
    required: true,
    select: {
        options: [
            { label: 'small', value: 'small' },
            { label: 'large', value: 'large' },
        ],
    },
};

const technicalAsset: ComponentProps<typeof EnvironmentSettingsSection>['technicalAsset'] = {
    id: 'ta-1',
    configuration: { name: 'PostgreSQLTechnicalAssetConfiguration' },
    environments: mockEnvironments.slice(0, 2).map((environment) => ({
        environment_id: environment.id,
        environment,
        creation_date: '',
    })),
    environment_values: { 'env-dev': { size: 'small' }, 'env-prd': { size: 'small' } },
};

function mockPlugins(requests: unknown[] = []) {
    server.use(
        http.get('*/api/v2/plugins', () =>
            HttpResponse.json({
                plugins: [
                    {
                        plugin: 'PostgreSQLTechnicalAssetConfiguration',
                        ui_metadata: [],
                        environment_ui_metadata: [
                            { environment_id: 'env-dev', ui_metadata: [sizeField] },
                            { environment_id: 'env-prd', ui_metadata: [sizeField] },
                        ],
                    },
                ],
            }),
        ),
        http.put('*/technical_assets/ta-1/environment_configuration', async ({ request }) => {
            requests.push(await request.json());
            return HttpResponse.json({ id: 'ta-1' });
        }),
        http.post('*/technical_assets/ta-1/environment_configuration/validate', () => HttpResponse.json(null)),
    );
}

describe('EnvironmentSettingsSection', () => {
    it('keeps Save disabled until something changes, then saves after confirming', async () => {
        const requests: unknown[] = [];
        mockPlugins(requests);
        renderWithProviders(
            <EnvironmentSettingsSection dataProductId="dp-1" technicalAsset={technicalAsset} canEdit />,
        );

        const save = await screen.findByRole('button', { name: 'Save' });
        expect(save).toBeDisabled();

        await userEvent.click(screen.getByLabelText('Size env-prd'));
        await userEvent.click(await screen.findByTitle('large'));
        expect(screen.getByText('Was small')).toBeInTheDocument();

        await userEvent.click(save);
        await userEvent.click(await screen.findByRole('button', { name: 'Save Changes' }));

        await waitFor(() =>
            expect(requests).toEqual([
                { environment_values: { 'env-dev': { size: 'small' }, 'env-prd': { size: 'large' } } },
            ]),
        );
    });

    it('shows backend errors on the cell', async () => {
        mockPlugins();
        server.use(
            http.put('*/technical_assets/ta-1/environment_configuration', () =>
                HttpResponse.json(
                    { detail: [{ environment_id: 'env-prd', field: 'size', message: 'Large is not allowed' }] },
                    { status: 422 },
                ),
            ),
        );
        renderWithProviders(
            <EnvironmentSettingsSection dataProductId="dp-1" technicalAsset={technicalAsset} canEdit />,
        );

        await userEvent.click(await screen.findByLabelText('Size env-prd'));
        await userEvent.click(await screen.findByTitle('large'));
        await userEvent.click(screen.getByRole('button', { name: 'Save' }));
        await userEvent.click(await screen.findByRole('button', { name: 'Save Changes' }));

        expect(await screen.findByText('Large is not allowed')).toBeInTheDocument();
    });

    it('validates a change without saving it', async () => {
        const saves: unknown[] = [];
        mockPlugins(saves);
        server.use(
            http.post('*/technical_assets/ta-1/environment_configuration/validate', () =>
                HttpResponse.json(
                    { detail: [{ environment_id: 'env-prd', field: 'size', message: 'Large is not allowed' }] },
                    { status: 422 },
                ),
            ),
        );
        renderWithProviders(
            <EnvironmentSettingsSection dataProductId="dp-1" technicalAsset={technicalAsset} canEdit />,
        );

        await userEvent.click(await screen.findByLabelText('Size env-prd'));
        await userEvent.click(await screen.findByTitle('large'));

        expect(await screen.findByText('Large is not allowed', {}, { timeout: 2000 })).toBeInTheDocument();
        expect(screen.getByRole('button', { name: 'Save' })).toBeDisabled();
        expect(saves).toEqual([]);
    });

    it('checks before opening the confirmation when Save is clicked right after a change', async () => {
        mockPlugins();
        server.use(
            http.post('*/technical_assets/ta-1/environment_configuration/validate', () =>
                HttpResponse.json(
                    { detail: [{ environment_id: 'env-prd', field: 'size', message: 'Large is not allowed' }] },
                    { status: 422 },
                ),
            ),
        );
        renderWithProviders(
            <EnvironmentSettingsSection dataProductId="dp-1" technicalAsset={technicalAsset} canEdit />,
        );

        await userEvent.click(await screen.findByLabelText('Size env-prd'));
        await userEvent.click(await screen.findByTitle('large'));
        await userEvent.click(screen.getByRole('button', { name: 'Save' }));

        expect(await screen.findByText('Large is not allowed')).toBeInTheDocument();
        expect(screen.queryByRole('button', { name: 'Save Changes' })).not.toBeInTheDocument();
    });

    it('is read-only without update permission', async () => {
        mockPlugins();
        renderWithProviders(
            <EnvironmentSettingsSection dataProductId="dp-1" technicalAsset={technicalAsset} canEdit={false} />,
        );

        await screen.findByText('Each Environment keeps its own value.');
        expect(screen.queryByRole('button', { name: 'Save' })).not.toBeInTheDocument();
    });

    it('shows an empty state when the plugin has no per-environment fields', async () => {
        mockPlugins();
        renderWithProviders(
            <EnvironmentSettingsSection
                dataProductId="dp-1"
                technicalAsset={{
                    ...technicalAsset,
                    configuration: { ...technicalAsset.configuration, name: 'Other' },
                }}
                canEdit
            />,
        );

        expect(await screen.findByText('No Settings')).toBeInTheDocument();
    });
});
