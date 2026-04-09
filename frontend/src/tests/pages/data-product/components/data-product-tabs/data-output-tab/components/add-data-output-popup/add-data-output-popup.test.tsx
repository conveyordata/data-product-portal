import { AddDataOutputPopup } from '@/pages/data-product/components/data-product-tabs/data-output-tab/components/add-data-output-popup/add-data-output-popup.tsx';
import { allowAllAuth } from '@/tests/mocks/auth.ts';
import { mockGetPlatformConfigs } from '@/tests/mocks/configuration.ts';
import { mock_data_products, mockDataProductHttp } from '@/tests/mocks/data_product.ts';
import { mockGetPlatformTiles, mockGetPlugins, mockRenderTechnicalAssetAccessPath } from '@/tests/mocks/plugins.ts';
import {
    mockGetResourceNamesConstraints,
    mockResourceNamesSanitize,
    mockResourceNamesValidate,
} from '@/tests/mocks/resource_names.ts';
import { mockGetTags } from '@/tests/mocks/tags.ts';
import { mockCreateTechnicalAsset } from '@/tests/mocks/technicalAssets.ts';
import { renderWithProviders, screen, userEvent, waitFor } from '@/tests/test-utils.tsx';

describe('TechnicalAssetPopup', async () => {
    it('should be able to fill in the whole form', async () => {
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
        mockCreateTechnicalAsset(mock_data_products[0].id);

        const user = userEvent.setup({ delay: null, pointerEventsCheck: 0 });
        const mockCloseFunction = vi.fn();
        renderWithProviders(
            <AddDataOutputPopup
                onClose={mockCloseFunction}
                isOpen
                dataProductId={mock_data_products[0].id}
                debounce={0}
            />,
        );

        const nameInput = screen.getByLabelText(/name/i);
        await waitFor(() => expect(nameInput).not.toBeDisabled());
        await user.type(nameInput, 'My new technical asset');

        const descriptionInput = screen.getByLabelText(/description/i);
        await user.type(descriptionInput, 'My new technical asset is the best one ever');

        await user.click(screen.getByLabelText(/aws/i));
        await user.click(screen.getByLabelText(/s3/i));
        await user.click(screen.getByLabelText(/bucket/i));

        await user.click(screen.getAllByText('datalake')[1]);
        await user.type(screen.getAllByRole('textbox', { name: /path/i })[0], 's3_path');

        const createButton = screen.getByRole('button', { name: /Create/i });
        await user.click(createButton);

        await waitFor(() => expect(mockCloseFunction).toHaveBeenCalled());
    }, 15000);
});
