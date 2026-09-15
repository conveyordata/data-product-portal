import { describe, expect, it } from 'vitest';
import { EventEntityType } from '@/store/api/services/generated/dataProductsApi.ts';
import i18n from '@/tests/i18n.ts';
import { renderWithProviders } from '@/tests/test-utils.tsx';
import { EventType } from '@/types/events/event-types.ts';
import {
    getEventTypeDisplayName,
    getEventTypeDisplayText,
    getNotificationDisplayName,
} from '@/utils/history.helper.tsx';

const t = i18n.t.bind(i18n);

describe('getEventTypeDisplayText', () => {
    it('shows expiring soon text for the new dataset link event', () => {
        i18n.addResource(
            'en',
            'translation',
            'EventDataProductDatasetLinkExpiringSoon',
            'Consuming link with the {{entity}} {{entity_type}} is expiring soon',
        );

        expect(
            getEventTypeDisplayText(
                t,
                EventType.DATA_PRODUCT_DATASET_LINK_EXPIRING_SOON,
                'Orders Output Port',
                EventEntityType.OutputPort,
            ),
        ).toBe('Consuming link with the Orders Output Port Output Port is expiring soon');
    });
});

describe('getNotificationDisplayName', () => {
    it('shows expiring soon notification text for the new dataset link event', () => {
        const { container } = renderWithProviders(
            <div>
                {getNotificationDisplayName(
                    t,
                    EventType.DATA_PRODUCT_DATASET_LINK_EXPIRING_SOON,
                    EventEntityType.OutputPort,
                    'Orders Output Port',
                    EventEntityType.DataProduct,
                    'Customer 360',
                    <span />,
                    <span />,
                )}
            </div>,
        );

        expect(container).toHaveTextContent(
            'Orders Output Port Output Port access for the Customer 360 Data Product is expiring soon',
        );
    });
});

describe('getEventTypeDisplayName', () => {
    it('shows expiring soon event history text for the new dataset link event', () => {
        const { container } = renderWithProviders(
            <div>
                {getEventTypeDisplayName(
                    t,
                    EventType.DATA_PRODUCT_DATASET_LINK_EXPIRING_SOON,
                    EventEntityType.OutputPort,
                    'Orders Output Port',
                    <span />,
                )}
            </div>,
        );

        expect(container).toHaveTextContent('Consuming link with the Orders Output Port Output Port is expiring soon');
    });
});
