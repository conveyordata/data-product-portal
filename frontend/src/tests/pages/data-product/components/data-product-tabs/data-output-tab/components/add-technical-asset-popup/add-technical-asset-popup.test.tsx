import type { UserEvent } from '@testing-library/user-event/dist/cjs/setup/setup.js';
import { AddTechnicalAssetPopup } from '@/pages/data-product/components/data-product-tabs/technical-asset-tab/components/add-technical-asset-popup/add-technical-asset-popup.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockAccessModesHttp } from '@/tests/mocks/configurationAccessModes.ts';
import { mockGetPlatformConfigs } from '@/tests/mocks/configurationPlatforms.ts';
import { mockDataProductHttp, mockDataProducts } from '@/tests/mocks/dataProducts.ts';
import { mockGetPlatformTiles, mockGetPlugins, mockRenderTechnicalAssetAccessPath } from '@/tests/mocks/plugins.ts';
import {
    mockGetResourceNamesConstraints,
    mockResourceNamesSanitize,
    mockResourceNamesValidate,
} from '@/tests/mocks/resource_names.ts';
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

        await waitFor(() => expect(screen.getByText('Read Only')).toBeInTheDocument());
        await user.click(screen.getByRole('checkbox', { name: /Select row 1/i }));

        const createButton = screen.getByRole('button', { name: /Create/i });
        await user.click(createButton);

        await waitFor(() => expect(mockCloseFunction).toHaveBeenCalled());
    }, 15000);

    it('should fail when specifying multiple access mode but no mode is selected from the table', async () => {
        defaultMocks();

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        renderWithProviders(
            <AddTechnicalAssetPopup onClose={vi.fn()} isOpen dataProductId={mockDataProducts[0].id} debounce={0} />,
        );

        await fillInNameAndDescription(user);

        await fillInS3(user);

        await user.click(screen.getByText('Configure access modes'));
        await waitFor(() => expect(screen.getByText('Read Only')).toBeInTheDocument());

        const createButton = screen.getByRole('button', { name: /Create/i });
        await user.click(createButton);

        await waitFor(() => expect(screen.getByText(/Please select at least one access mode/i)).toBeInTheDocument());
    }, 15000);
});
