import type { UserEvent } from '@testing-library/user-event/dist/cjs/setup/setup.js';
import { delay, HttpResponse, http } from 'msw';
import { AddTechnicalAssetPopup } from '@/pages/data-product/components/data-product-tabs/technical-asset-tab/components/add-technical-asset-popup/add-technical-asset-popup.tsx';
import type { RenderTechnicalAssetAccessPathRequest } from '@/store/api/services/generated/pluginsApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockAccessModesHttp } from '@/tests/mocks/configurationAccessModes.ts';
import { mock_platform_service_configuration, mockGetPlatformConfigs } from '@/tests/mocks/configurationPlatforms.ts';
import { mockDataProductHttp, mockDataProducts } from '@/tests/mocks/dataProducts.ts';
import {
    mock_platform_tiles,
    mock_plugins,
    mockGetPlatformTiles,
    mockGetPlugins,
    mockRenderTechnicalAssetAccessPath,
} from '@/tests/mocks/plugins.ts';
import {
    mockGetResourceNamesConstraints,
    mockResourceNamesSanitize,
    mockResourceNamesValidate,
} from '@/tests/mocks/resource_names.ts';
import { server } from '@/tests/mocks/server.ts';
import { mockGetTags } from '@/tests/mocks/tags.ts';
import { mockCreateTechnicalAsset } from '@/tests/mocks/technicalAssets.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

const defaultMocks = () => {
    allowAllAuth();
    mockDataProductHttp();
    mockGetPlugins();
    mockGetTags();
    mockGetPlatformTiles();
    mockGetPlatformConfigs();
    mockGetResourceNamesConstraints();
    mockResourceNamesSanitize();
    mockResourceNamesValidate();
    mockRenderTechnicalAssetAccessPath();
    mockAccessModesHttp();
};

describe('TechnicalAssetPopup', async () => {
    const fillInS3 = async (user: UserEvent) => {
        await user.click(screen.getByLabelText(/aws/i));
        await user.click(screen.getByLabelText(/s3/i));
        await user.click(screen.getByLabelText(/bucket/i));

        await user.click(screen.getAllByText('datalake')[1]);
        await user.type(screen.getAllByRole('textbox', { name: /path/i })[0], 's3_path');
    };

    const fillInGitHub = async (user: UserEvent) => {
        await user.click(screen.getByLabelText(/github/i));
        await user.type(screen.getByLabelText(/^repository$/i), 'my-org/my-repo');
    };

    const fillInNameAndDescription = async (user: UserEvent) => {
        const nameInput = screen.getByLabelText(/name/i);
        await waitFor(() => expect(nameInput).not.toBeDisabled());
        await user.type(nameInput, 'My new technical asset');

        const descriptionInput = screen.getByLabelText(/description/i);
        await user.type(descriptionInput, 'My new technical asset is the best one ever');
    };

    it('should be able to fill in the whole form', async () => {
        defaultMocks();
        mockCreateTechnicalAsset(mockDataProducts[0].id);

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        const mockCloseFunction = vi.fn();
        renderWithProviders(
            <AddTechnicalAssetPopup
                onClose={mockCloseFunction}
                isOpen
                dataProductId={mockDataProducts[0].id}
                debounce={0}
            />,
        );

        await fillInNameAndDescription(user);
        await fillInS3(user);

        const createButton = screen.getByRole('button', { name: /Create/i });
        await user.click(createButton);

        await waitFor(() => expect(mockCloseFunction).toHaveBeenCalled());
    }, 15000);

    it('should be able to select multiple access modes and choose specific modes', async () => {
        defaultMocks();
        mockCreateTechnicalAsset(mockDataProducts[0].id);

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        const mockCloseFunction = vi.fn();
        renderWithProviders(
            <AddTechnicalAssetPopup
                onClose={mockCloseFunction}
                isOpen
                dataProductId={mockDataProducts[0].id}
                debounce={0}
            />,
        );

        await fillInNameAndDescription(user);
        await fillInS3(user);

        await user.click(screen.getByText('Configure access modes'));

        expect(await screen.findByText('Read Only')).toBeInTheDocument();
        await user.click(screen.getAllByLabelText('Select row')[0]);

        const createButton = screen.getByRole('button', { name: /Create/i });
        await user.click(createButton);

        await waitFor(() => expect(mockCloseFunction).toHaveBeenCalled());
    }, 15000);

    it('should not show access mode choice when no access mode matches the selected technical asset type', async () => {
        defaultMocks();
        mockAccessModesHttp([
            {
                id: '1',
                name: 'Read Only',
                description: 'Read-only access to data',
                technical_asset_types: ['SnowflakeTechnicalAssetConfiguration'],
            },
        ]);

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderWithProviders(
            <AddTechnicalAssetPopup onClose={vi.fn()} isOpen dataProductId={mockDataProducts[0].id} debounce={0} />,
        );

        await fillInNameAndDescription(user);

        await fillInS3(user);

        await waitFor(() => {
            expect(screen.queryByText('Single access mode')).not.toBeInTheDocument();
            expect(screen.queryByText('Configure access modes')).not.toBeInTheDocument();
        });
    }, 15000);

    it('should clear the result and skip rendering the access path for a plugin without a platform', async () => {
        defaultMocks();
        const renderSpy = vi.fn();
        server.use(
            http.post('*/api/v2/plugins/render_technical_asset_access_path', () => {
                renderSpy();
                return HttpResponse.json({ technical_asset_access_path: 'should-not-be-used' });
            }),
        );

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderWithProviders(
            <AddTechnicalAssetPopup onClose={vi.fn()} isOpen dataProductId={mockDataProducts[0].id} debounce={0} />,
        );

        await fillInNameAndDescription(user);
        await fillInGitHub(user);

        await waitFor(() => expect(screen.getByLabelText(/repository link/i)).toHaveValue(''));
        expect(renderSpy).not.toHaveBeenCalled();
    }, 15000);

    it('should refresh the preview when only the name changes', async () => {
        defaultMocks();
        mockResourceNamesSanitize('fixed-namespace');
        const previewRequests = vi.fn();
        server.use(
            http.post<never, RenderTechnicalAssetAccessPathRequest>(
                '*/api/v2/plugins/render_technical_asset_access_path',
                async ({ request }) => {
                    const body = await request.json();
                    previewRequests(body);
                    return HttpResponse.json({ technical_asset_access_path: body.name });
                },
            ),
        );

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderWithProviders(
            <AddTechnicalAssetPopup onClose={vi.fn()} isOpen dataProductId={mockDataProducts[0].id} debounce={0} />,
        );
        await fillInNameAndDescription(user);
        await fillInS3(user);
        await waitFor(() => expect(screen.getByLabelText(/resulting path/i)).toHaveValue('My new technical asset'));

        const nameInput = screen.getByLabelText(/^name$/i);
        await user.clear(nameInput);
        await user.type(nameInput, 'Renamed asset');

        await waitFor(() => expect(screen.getByLabelText(/resulting path/i)).toHaveValue('Renamed asset'));
        expect(previewRequests).toHaveBeenLastCalledWith(
            expect.objectContaining({ name: 'Renamed asset', namespace: 'fixed-namespace' }),
        );
    }, 15000);

    it('should initialize previews only after selecting a child plugin, including when switching platforms', async () => {
        defaultMocks();
        mockResourceNamesSanitize('fixed-namespace');
        const platform = { id: 'test-platform', name: 'Test Platform' };
        mockGetPlatformConfigs({
            platform_service_configurations: [
                ...mock_platform_service_configuration,
                {
                    id: 'test-config',
                    platform,
                    service: {
                        id: 'test-service',
                        name: 'test-plugin',
                        platform,
                        result_string_template: 'rendered-preview',
                        technical_info_template: 'rendered-preview',
                    },
                    config: [],
                },
            ],
        });
        mockGetPlugins({
            plugins: [
                ...mock_plugins,
                {
                    plugin: 'TestTechnicalAssetConfiguration',
                    ui_metadata: [],
                    has_environments: true,
                    platform: 'test-plugin',
                    parent_platform: 'test-platform',
                    display_name: 'Test Plugin',
                    detailed_name: 'Test Plugin',
                    icon_name: '',
                    result_label: 'Resulting path',
                },
            ],
        });
        mockGetPlatformTiles({
            platform_tiles: [
                ...mock_platform_tiles,
                {
                    label: 'Test Platform',
                    value: 'test-platform',
                    icon_name: '',
                    children: [
                        {
                            label: 'Test Plugin',
                            value: 'test-plugin',
                            icon_name: '',
                        },
                    ],
                    show_in_form: true,
                },
            ],
        });
        const previewRequests = vi.fn();
        server.use(
            http.post<never, RenderTechnicalAssetAccessPathRequest>(
                '*/api/v2/plugins/render_technical_asset_access_path',
                async ({ request }) => {
                    const body = await request.json();
                    previewRequests(body);
                    return HttpResponse.json({ technical_asset_access_path: 'rendered-preview' });
                },
            ),
        );

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderWithProviders(
            <AddTechnicalAssetPopup onClose={vi.fn()} isOpen dataProductId={mockDataProducts[0].id} debounce={0} />,
        );
        const nameInput = screen.getByLabelText(/^name$/i);
        await waitFor(() => expect(nameInput).not.toBeDisabled());
        await user.type(nameInput, 'test-asset');
        await screen.findByDisplayValue('fixed-namespace');

        await user.click(screen.getByLabelText(/^test platform$/i));
        await user.click(screen.getByLabelText(/^test plugin$/i));

        await waitFor(() => expect(screen.getByLabelText('Resulting path')).toHaveValue('rendered-preview'));
        expect(previewRequests).toHaveBeenLastCalledWith(
            expect.objectContaining({
                name: 'test-asset',
                namespace: 'fixed-namespace',
                data_product_id: mockDataProducts[0].id,
                platform_id: platform.id,
                service_id: 'test-service',
                configuration: { name: 'TestTechnicalAssetConfiguration' },
            }),
        );

        await waitFor(() => expect(screen.getByLabelText(/^aws$/i)).not.toBeDisabled());
        await user.click(screen.getByLabelText(/^aws$/i));
        expect(screen.queryByLabelText('Resulting path')).not.toBeInTheDocument();
        await user.click(screen.getByLabelText(/^s3$/i));
        expect(screen.getByLabelText('Resulting path')).toHaveValue('');
        await user.click(screen.getByLabelText(/^bucket$/i));
        await user.click(screen.getAllByText('datalake')[1]);
        await user.type(screen.getByLabelText(/^path$/i), 'test-path');

        await waitFor(() => expect(screen.getByLabelText('Resulting path')).toHaveValue('rendered-preview'));
        const awsConfig = mock_platform_service_configuration[0];
        expect(previewRequests).toHaveBeenLastCalledWith(
            expect.objectContaining({
                platform_id: awsConfig.platform.id,
                service_id: awsConfig.service.id,
                configuration: expect.objectContaining({ name: 'S3TechnicalAssetConfiguration', path: 'test-path' }),
            }),
        );

        await waitFor(() => expect(screen.getByLabelText(/^test platform$/i)).not.toBeDisabled());
        await user.click(screen.getByLabelText(/^test platform$/i));
        expect(screen.queryByLabelText('Resulting path')).not.toBeInTheDocument();
        await user.click(screen.getByLabelText(/^test plugin$/i));
        await waitFor(() => expect(screen.getByLabelText('Resulting path')).toHaveValue('rendered-preview'));

        for (const [request] of previewRequests.mock.calls) {
            const isTestPlatform = request.platform_id === platform.id;
            expect(request.service_id).toBe(isTestPlatform ? 'test-service' : awsConfig.service.id);
            expect(request.configuration).toEqual(
                expect.objectContaining({
                    name: isTestPlatform ? 'TestTechnicalAssetConfiguration' : 'S3TechnicalAssetConfiguration',
                }),
            );
        }
    }, 15000);

    it('should block switching platforms while a render request is in flight', async () => {
        defaultMocks();
        server.use(
            http.post('*/api/v2/plugins/render_technical_asset_access_path', async () => {
                await delay(200);
                return HttpResponse.json({ technical_asset_access_path: 's3-path' });
            }),
        );

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderWithProviders(
            <AddTechnicalAssetPopup onClose={vi.fn()} isOpen dataProductId={mockDataProducts[0].id} debounce={0} />,
        );

        await fillInNameAndDescription(user);
        await fillInS3(user);

        await waitFor(() => expect(screen.getByLabelText(/github/i)).toBeDisabled());

        await waitFor(() => expect(screen.getByLabelText(/github/i)).not.toBeDisabled(), { timeout: 2000 });
    }, 15000);

    it('should scroll to the first invalid field when submitting an incomplete form', async () => {
        defaultMocks();

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        const mockCloseFunction = vi.fn();
        renderWithProviders(
            <AddTechnicalAssetPopup
                onClose={mockCloseFunction}
                isOpen
                dataProductId={mockDataProducts[0].id}
                debounce={0}
            />,
        );

        const nameInput = screen.getByLabelText(/name/i);
        await waitFor(() => expect(nameInput).not.toBeDisabled());

        const createButton = screen.getByRole('button', { name: /Create/i });
        await user.click(createButton);

        expect(await screen.findByText('Please provide the name of the Technical Asset')).toBeInTheDocument();
        expect(screen.getByText('Please provide a description for the Technical Asset')).toBeInTheDocument();
        expect(mockCloseFunction).not.toHaveBeenCalled();
    }, 15000);
});
