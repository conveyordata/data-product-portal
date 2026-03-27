import { TeamTab } from '@/pages/data-product/components/data-product-tabs/team-tab/team-tab.tsx';
import { renderWithProviders } from '@/tests/test-utils.tsx';

describe('TeamTab', () => {
    it('should filter out the users', async () => {
        renderWithProviders(<TeamTab dataProductId={'bla'} />);
    });
});
