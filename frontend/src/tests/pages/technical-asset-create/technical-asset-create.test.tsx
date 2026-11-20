import type { UserEvent } from '@testing-library/user-event/dist/cjs/setup/setup.js';
import { delay, HttpResponse, http } from 'msw';
import { Route, Routes } from 'react-router';
import { TechnicalAssetCreate } from '@/pages/technical-asset-create/technical-asset-create.page.tsx';
import { ResourceNameModel, ResourceNameValidityType } from '@/store/api/services/generated/resourceNamesApi.ts';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockAccessModesHttp } from '@/tests/mocks/configurationAccessModes.ts';
import { mockGetPlatformConfigs } from '@/tests/mocks/configurationPlatforms.ts';
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

    it('should be able to select multiple access modes and choose specific modes', async () => {
        defaultMocks();
        mockCreateTechnicalAsset(mockDataProducts[0].id);

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        await fillInNameAndDescription(user);
        await fillInS3(user);

        await user.click(screen.getByText('Configure access modes'));

        expect(await screen.findByText('Read Only')).toBeInTheDocument();
        await user.click(screen.getAllByLabelText('Select row')[0]);

        const createButton = screen.getByRole('button', { name: /Create/i });
        await user.click(createButton);

        expect(await screen.findByText('Technical asset detail')).toBeInTheDocument();
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
        renderPage();

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

    it('should scroll to the first invalid field when submitting an incomplete form', async () => {
        defaultMocks();

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderPage();

        const nameInput = screen.getByLabelText(/name/i);
        await waitFor(() => expect(nameInput).not.toBeDisabled());

        const createButton = screen.getByRole('button', { name: /Create/i });
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
