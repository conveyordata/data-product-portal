import { describe, it } from 'vitest';
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
        const mockCloseFunction = vi.fn();
        renderWithProviders(
            <AddDataOutputPopup onClose={mockCloseFunction} isOpen dataProductId={mock_data_products[0].id} />,
        );
        const nameInput = await waitFor(() => {
            const input = screen.getByRole('textbox', { name: /name/i });
            expect(input).not.toBeDisabled();
            return input;
        });
        await userEvent.type(nameInput, 'My new technical asset');

        const descriptionInput = screen.getByRole('textbox', { name: /description/i });
        await userEvent.type(descriptionInput, 'My new technical asset is the best one ever');

        const awsRadio = screen.getByRole('radio', { name: /aws/i });
        await userEvent.click(awsRadio, { pointerEventsCheck: 0 });

        const s3Radio = screen.getByRole('radio', { name: /s3/i });
        await userEvent.click(s3Radio, { pointerEventsCheck: 0 });

        const bucketInput = screen.getByRole('combobox', { name: /bucket/i });
        await userEvent.click(bucketInput);
        await userEvent.click(screen.getAllByText('datalake')[1]);

        await userEvent.type(screen.getAllByRole('textbox', { name: /path/i })[0], 's3_path');

        const createButton = screen.getByRole('button', { name: /Create/i });
        await userEvent.click(createButton);

        await waitFor(() => expect(mockCloseFunction).toHaveBeenCalled());
    }, 15000);
});
