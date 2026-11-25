import type { UserEvent } from '@testing-library/user-event/dist/cjs/setup/setup.js';
import { delay, HttpResponse, http } from 'msw';
import { Route, Routes } from 'react-router';
import { TechnicalAssetCreate } from '@/pages/technical-asset-create/technical-asset-create.page.tsx';
import type { RenderTechnicalAssetAccessPathRequest } from '@/store/api/services/generated/pluginsApi.ts';
import { ResourceNameModel, ResourceNameValidityType } from '@/store/api/services/generated/resourceNamesApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockAccessModes, mockAccessModesHttp } from '@/tests/mocks/configurationAccessModes.ts';
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

const renderPage = () =>
    renderWithProviders(
        <Routes>
            <Route path="/studio/:dataProductId/technical-assets/new" element={<TechnicalAssetCreate debounce={0} />} />
            <Route path="/studio/:dataProductId/:dataOutputId" element={<div>Technical asset detail</div>} />
            <Route path="/studio/:dataProductId" element={<div>Data Product page</div>} />
        </Routes>,
        { routerProps: { initialEntries: [`/studio/${mockDataProducts[0].id}/technical-assets/new`] } },
    );

const mockNamespaceLengths = () => {
    mockGetPlugins({
        plugins: mock_plugins.map((plugin) =>
            plugin.platform === 's3' ? { ...plugin, namespace_max_length: 24 } : plugin,
        ),
    });
    const validations = vi.fn();
    server.use(
        http.get('*/api/v2/resource_names/sanitize', async ({ request }) => {
            const params = new URL(request.url).searchParams;
            const limit = params.get('technical_asset_type') === 'S3TechnicalAssetConfiguration' ? 24 : 64;
            await delay(50);
            return HttpResponse.json({
                resource_name: params.get('name')?.toLowerCase().replace(/ /g, '-').slice(0, limit),
            });
        }),
        http.get('*/api/v2/resource_names/validate', ({ request }) => {
            const params = Object.fromEntries(new URL(request.url).searchParams);
            validations(params);
            const limit = params.technical_asset_type === 'S3TechnicalAssetConfiguration' ? 24 : 64;
            return HttpResponse.json({
                validity: params.resource_name.length > limit ? 'INVALID_LENGTH' : 'VALID',
            });
        }),
    );
    return validations;
};

describe('TechnicalAssetCreate', async () => {
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
        renderPage();

        await fillInNameAndDescription(user);
        await fillInS3(user);

        const createButton = screen.getByRole('button', { name: /Create/i });
        await user.click(createButton);

        expect(await screen.findByText('Technical asset detail')).toBeInTheDocument();
    }, 15000);

    it.each(['owner/repository', undefined])('renders an optional plugin placeholder: %s', async (placeholder) => {
        defaultMocks();
        mockGetPlugins({
            plugins: mock_plugins.map((plugin) =>
                plugin.platform === 'github'
                    ? {
                          ...plugin,
                          ui_metadata: plugin.ui_metadata.map((field) => ({
                              ...field,
                              string: { ...field.string, placeholder },
                          })),
                      }
                    : plugin,
            ),
        });
        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();
        const github = await screen.findByLabelText(/^github$/i);
        await waitFor(() => expect(github).toBeEnabled());
        await user.click(github);

        const input = screen.getByLabelText(/^repository$/i);
        if (placeholder) {
            expect(input).toHaveAttribute('placeholder', placeholder);
        } else {
            expect(input).not.toHaveAttribute('placeholder');
        }
        expect(input).toHaveValue('');
        await user.type(input, 'my-org/my-repo');
        expect(input).toHaveValue('my-org/my-repo');
    });

    it('should preselect the default access mode and send the selected access modes', async () => {
        defaultMocks();
        const requests = vi.fn();
        server.use(
            http.post(`*/api/v2/data_products/${mockDataProducts[0].id}/technical_assets`, async ({ request }) => {
                requests(await request.json());
                return HttpResponse.json({ id: '1' });
            }),
        );

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        await fillInNameAndDescription(user);
        await fillInS3(user);

        expect(await screen.findByLabelText('Row selected')).toBeChecked();
        const readWrite = screen.getByLabelText('Select row');
        expect(readWrite).not.toBeChecked();
        await user.click(readWrite);

        await user.click(screen.getByText('Create'));

        expect(await screen.findByText('Technical asset detail')).toBeInTheDocument();
        expect(requests).toHaveBeenCalledWith(expect.objectContaining({ access_mode_ids: ['1', '2'] }));
    }, 15000);

    it('should preselect the default again when switching to a type with the same default', async () => {
        defaultMocks();
        mockAccessModesHttp([
            {
                ...mockAccessModes[0],
                technical_asset_types: ['S3TechnicalAssetConfiguration', 'GitHubPlugin'],
                default_for_technical_asset_types: ['S3TechnicalAssetConfiguration', 'GitHubPlugin'],
            },
            mockAccessModes[1],
        ]);
        const requests = vi.fn();
        server.use(
            http.post(`*/api/v2/data_products/${mockDataProducts[0].id}/technical_assets`, async ({ request }) => {
                requests(await request.json());
                return HttpResponse.json({ id: '1' });
            }),
        );

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        await fillInNameAndDescription(user);
        await fillInS3(user);
        await user.click(await screen.findByLabelText('Select row'));
        expect(screen.getAllByLabelText('Row selected')).toHaveLength(2);

        await waitFor(() => expect(screen.getByLabelText(/^github$/i)).toBeEnabled());
        await fillInGitHub(user);
        await waitFor(() => expect(screen.getByText('Create').closest('button')).toBeEnabled());
        await user.click(screen.getByText('Create'));

        expect(await screen.findByText('Technical asset detail')).toBeInTheDocument();
        expect(requests).toHaveBeenCalledWith(expect.objectContaining({ access_mode_ids: ['1'] }));
    }, 15000);

    it('should require at least one access mode', async () => {
        defaultMocks();
        mockCreateTechnicalAsset(mockDataProducts[0].id);

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        await fillInNameAndDescription(user);
        await fillInS3(user);

        await user.click(await screen.findByLabelText('Row selected'));
        await user.click(screen.getByText('Create'));

        expect(await screen.findByText('Please select at least one access mode')).toBeInTheDocument();
        expect(screen.queryByText('Technical asset detail')).not.toBeInTheDocument();
    }, 15000);

    it('should not show access modes when no access mode matches the selected technical asset type', async () => {
        defaultMocks();
        mockAccessModesHttp([
            {
                id: '1',
                name: 'Read Only',
                description: 'Read-only access to data',
                technical_asset_types: ['SnowflakeTechnicalAssetConfiguration'],
                default_for_technical_asset_types: ['SnowflakeTechnicalAssetConfiguration'],
                in_use_technical_asset_types: [],
            },
        ]);

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        await fillInNameAndDescription(user);

        await fillInS3(user);

        await waitFor(() => {
            expect(screen.queryByText('Access modes')).not.toBeInTheDocument();
            expect(screen.queryByText('Read Only')).not.toBeInTheDocument();
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
        renderPage();

        await fillInNameAndDescription(user);
        await fillInGitHub(user);

        await waitFor(() => expect(screen.getByLabelText(/repository link/i)).toHaveValue(''));
        expect(renderSpy).not.toHaveBeenCalled();
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
        renderPage();

        await fillInNameAndDescription(user);
        await fillInS3(user);

        await waitFor(() => expect(screen.getByLabelText(/github/i)).toBeDisabled());

        await waitFor(() => expect(screen.getByLabelText(/github/i)).not.toBeDisabled(), { timeout: 2000 });
    }, 15000);

    it('uses the selected type for namespace length, suggestions and uniqueness', async () => {
        defaultMocks();
        const validations = mockNamespaceLengths();
        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();
        const name = 'A technical asset name longer than twenty four characters';
        const fullNamespace = name.toLowerCase().replace(/ /g, '-');
        const input = await screen.findByLabelText(/^name$/i);
        await waitFor(() => expect(input).toBeEnabled());
        await user.type(input, name);

        const namespace = await screen.findByDisplayValue(fullNamespace);
        expect(namespace).toHaveAttribute('maxlength', '64');
        expect(validations).not.toHaveBeenCalled();

        await user.click(screen.getByLabelText(/^aws$/i));
        await user.click(screen.getByLabelText(/^s3$/i));
        expect(screen.getByText('Create', { selector: 'button span' }).closest('button')).toBeDisabled();
        await waitFor(() => expect(namespace).toHaveValue(fullNamespace.slice(0, 24)));
        expect(namespace).toHaveAttribute('maxlength', '24');
        await waitFor(() =>
            expect(validations).toHaveBeenLastCalledWith({
                model: 'technical_asset',
                technical_asset_type: 'S3TechnicalAssetConfiguration',
                data_product_id: mockDataProducts[0].id,
                resource_name: fullNamespace.slice(0, 24),
            }),
        );
        await waitFor(() => expect(screen.getByText('Create').closest('button')).toBeEnabled());

        await user.click(screen.getByLabelText(/^github$/i));
        await waitFor(() => expect(namespace).toHaveValue(fullNamespace));
        expect(namespace).toHaveAttribute('maxlength', '64');
        await waitFor(() =>
            expect(validations).toHaveBeenLastCalledWith(
                expect.objectContaining({ technical_asset_type: 'GitHubPlugin', resource_name: fullNamespace }),
            ),
        );
    }, 15000);

    it('preserves a manually entered namespace and revalidates it when the type changes', async () => {
        defaultMocks();
        mockNamespaceLengths();
        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();
        await fillInNameAndDescription(user);
        const namespace = await screen.findByDisplayValue('my-new-technical-asset');
        await user.click(screen.getByLabelText('edit'));
        await user.clear(namespace);
        await user.type(namespace, 'manually-entered-namespace-longer-than-24');

        await user.click(screen.getByLabelText(/^aws$/i));
        await user.click(screen.getByLabelText(/^s3$/i));

        expect(namespace).toHaveValue('manually-entered-namespace-longer-than-24');
        expect(await screen.findByText('Namespace is too long')).toBeInTheDocument();

        await user.click(screen.getByLabelText(/^github$/i));
        await waitFor(() => expect(screen.queryByText('Namespace is too long')).not.toBeInTheDocument());
        expect(namespace).toHaveValue('manually-entered-namespace-longer-than-24');
    }, 15000);

    it('renders previews only for the selected child after switching platforms', async () => {
        defaultMocks();
        const awsConfig = mock_platform_service_configuration[0];
        mockGetPlatformConfigs({
            platform_service_configurations: [
                ...mock_platform_service_configuration,
                {
                    ...awsConfig,
                    id: 'glue-config',
                    service: { ...awsConfig.service, id: 'glue-service', name: 'Glue' },
                    config: [],
                },
            ],
        });
        mockGetPlugins({
            plugins: [
                ...mock_plugins,
                {
                    ...mock_plugins[0],
                    plugin: 'GlueTechnicalAssetConfiguration',
                    platform: 'glue',
                    display_name: 'Glue',
                    detailed_name: 'Glue',
                    ui_metadata: [],
                },
            ],
        });
        const previews = vi.fn();
        server.use(
            http.post<never, RenderTechnicalAssetAccessPathRequest>(
                '*/api/v2/plugins/render_technical_asset_access_path',
                async ({ request }) => {
                    previews(await request.json());
                    return HttpResponse.json({ technical_asset_access_path: 'preview' });
                },
            ),
        );
        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();
        await fillInNameAndDescription(user);
        await user.click(screen.getByLabelText(/^aws$/i));
        expect(previews).not.toHaveBeenCalled();
        await user.click(screen.getByLabelText(/^glue$/i));
        await waitFor(() => expect(screen.getByLabelText('Resulting path')).toHaveValue('preview'));

        await waitFor(() => expect(screen.getByLabelText(/^github$/i)).toBeEnabled());
        await user.click(screen.getByLabelText(/^github$/i));
        const count = previews.mock.calls.length;
        await waitFor(() => expect(screen.getByLabelText(/^aws$/i)).toBeEnabled());
        await user.click(screen.getByLabelText(/^aws$/i));
        expect(screen.queryByLabelText('Resulting path')).not.toBeInTheDocument();
        await user.click(screen.getByLabelText(/^s3$/i));
        expect(screen.getByLabelText('Resulting path')).toHaveValue('');
        expect(previews).toHaveBeenCalledTimes(count);
        await user.click(screen.getByLabelText(/^bucket$/i));
        await user.click(screen.getAllByText('datalake')[1]);
        await user.type(screen.getByLabelText(/^path$/i), 'test-path');

        await waitFor(() => expect(screen.getByLabelText('Resulting path')).toHaveValue('preview'));
        expect(previews).toHaveBeenLastCalledWith(
            expect.objectContaining({
                platform_id: awsConfig.platform.id,
                service_id: awsConfig.service.id,
                configuration: expect.objectContaining({ name: 'S3TechnicalAssetConfiguration', path: 'test-path' }),
            }),
        );
        for (const [request] of previews.mock.calls) {
            expect(request.configuration.name).toBe(
                request.service_id === 'glue-service'
                    ? 'GlueTechnicalAssetConfiguration'
                    : 'S3TechnicalAssetConfiguration',
            );
        }
    }, 15000);

    it('should scroll to the first invalid field when submitting an incomplete form', async () => {
        defaultMocks();

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        const nameInput = screen.getByLabelText(/name/i);
        await waitFor(() => expect(nameInput).not.toBeDisabled());

        const createButton = screen.getByRole('button', { name: /Create/i });
        await waitFor(() => expect(createButton).toBeEnabled());
        await user.click(createButton);

        expect(await screen.findByText('Please provide the name of the Technical Asset')).toBeInTheDocument();
        expect(screen.getByText('Please provide a description for the Technical Asset')).toBeInTheDocument();
        expect(screen.queryByText('Technical asset detail')).not.toBeInTheDocument();
    }, 15000);

    it('should check the namespace against the Technical Assets of the selected type and recheck it when the type changes', async () => {
        defaultMocks();
        mockGetPlugins({
            plugins: [
                ...mock_plugins,
                {
                    ...mock_plugins[0],
                    ui_metadata: [],
                    plugin: 'GlueTechnicalAssetConfiguration',
                    platform: 'glue',
                    display_name: 'Glue',
                    detailed_name: 'Database',
                },
            ],
        });
        const validations: URLSearchParams[] = [];
        server.use(
            http.get('*/api/v2/resource_names/validate', ({ request }) => {
                const params = new URL(request.url).searchParams;
                validations.push(params);
                return HttpResponse.json({
                    validity:
                        params.get('technical_asset_type') === 'S3TechnicalAssetConfiguration'
                            ? ResourceNameValidityType.Duplicate
                            : ResourceNameValidityType.Valid,
                });
            }),
        );
        const lastValidation = () => validations[validations.length - 1];

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        await fillInNameAndDescription(user);
        await fillInS3(user);

        expect(await screen.findByText('This namespace is already in use')).toBeInTheDocument();
        expect(lastValidation()?.get('model')).toBe(ResourceNameModel.TechnicalAsset);
        expect(lastValidation()?.get('data_product_id')).toBe(mockDataProducts[0].id);
        expect(lastValidation()?.get('technical_asset_type')).toBe('S3TechnicalAssetConfiguration');

        await waitFor(() => expect(screen.getByLabelText(/glue/i)).not.toBeDisabled());
        await user.click(screen.getByLabelText(/glue/i));

        await waitFor(() =>
            expect(lastValidation()?.get('technical_asset_type')).toBe('GlueTechnicalAssetConfiguration'),
        );
        await waitFor(() => expect(screen.queryByText('This namespace is already in use')).not.toBeInTheDocument());
    }, 15000);

    it('should clear the namespace check when the Technical Asset Type is cleared', async () => {
        defaultMocks();
        mockGetPlatformTiles({
            platform_tiles: [
                ...mock_platform_tiles,
                {
                    ...mock_platform_tiles[0],
                    label: 'Azure',
                    value: 'azure',
                    children: mock_platform_tiles[0].children?.slice(0, 1),
                },
            ],
        });
        server.use(
            http.get('*/api/v2/resource_names/validate', () =>
                HttpResponse.json({ validity: ResourceNameValidityType.Duplicate }),
            ),
        );

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        await fillInNameAndDescription(user);
        await fillInS3(user);
        expect(await screen.findByText('This namespace is already in use')).toBeInTheDocument();

        await waitFor(() => expect(screen.getByLabelText(/azure/i)).not.toBeDisabled());
        await user.click(screen.getByLabelText(/azure/i));

        await waitFor(() => expect(screen.queryByText('This namespace is already in use')).not.toBeInTheDocument());
    }, 15000);

    it('should not check the namespace before a Technical Asset Type is selected', async () => {
        defaultMocks();
        const validations: URLSearchParams[] = [];
        server.use(
            http.get('*/api/v2/resource_names/validate', ({ request }) => {
                validations.push(new URL(request.url).searchParams);
                return HttpResponse.json({ validity: ResourceNameValidityType.Valid });
            }),
        );

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        await fillInNameAndDescription(user);

        await waitFor(() => expect(document.querySelector('[data-cy="namespace"]')).not.toHaveValue(''));
        expect(validations).toHaveLength(0);
        expect(document.querySelector('.ant-form-item-feedback-icon-success')).not.toBeInTheDocument();
    }, 15000);

    it('should render the page title and the Technical Asset Type', async () => {
        defaultMocks();

        renderPage();

        expect(await screen.findByText('New Technical Asset')).toBeInTheDocument();
        await waitFor(() => expect(screen.getByLabelText(/name/i)).not.toBeDisabled());

        expect(screen.getByText('Technical Asset Type')).toBeInTheDocument();
    }, 15000);

    it('should go back to the Data Product when cancelling', async () => {
        defaultMocks();

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        const cancelButton = await screen.findByRole('button', { name: /Cancel/i });
        await waitFor(() => expect(cancelButton).not.toBeDisabled());
        await user.click(cancelButton);

        expect(await screen.findByText('Data Product page')).toBeInTheDocument();
    }, 15000);
});
