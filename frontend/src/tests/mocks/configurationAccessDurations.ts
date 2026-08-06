import { HttpResponse, http } from 'msw';
import {
    AbstractDataProductType,
    type AccessDuration,
    AccessDurationType,
} from '@/store/api/services/generated/configurationAccessDurationsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mockAccessDurations: AccessDuration[] = [
    {
        id: '1',
        abstract_data_product_type: AbstractDataProductType.DataProducts,
        access_duration_type: AccessDurationType.Permanent,
        days: null,
        is_default: true,
    },
    {
        id: '2',
        abstract_data_product_type: AbstractDataProductType.Explorations,
        access_duration_type: AccessDurationType.TimeBound,
        days: 30,
        is_default: true,
    },
];

const endpoint = '*/api/v2/configuration/access_durations';
export const mockAccessDurationsGet = (accessDurations: AccessDuration[] = mockAccessDurations) => {
    server.use(http.get(endpoint, () => HttpResponse.json(accessDurations)));
};

export const mockUpdateAccessDuration = (savedAccessDurations: AccessDuration[] = mockAccessDurations) => {
    server.use(
        http.put('*/api/v2/configuration/access_durations/:abstractDataProductType', () => {
            return HttpResponse.json(savedAccessDurations);
        }),
    );
};
