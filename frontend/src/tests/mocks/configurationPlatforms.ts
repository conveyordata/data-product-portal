import { HttpResponse, http } from 'msw';
import type {
    GetAllPlatformServiceConfigurationsResponse,
    PlatformServiceConfiguration,
} from '@/store/api/services/generated/configurationPlatformsApi.ts';
import { server } from '@/tests/mocks/server.ts';
export const mock_platform_service_configuration: PlatformServiceConfiguration[] = [
    {
        id: '6bd82fd6-9a23-4517-a07c-9110d83ab38f',
        platform: {
            id: '76b648e3-dc59-4c21-8dc7-997490052ea9',
            name: 'AWS',
        },
        service: {
            id: 'c8972e04-d28d-4a3b-8574-c1c831be88a9',
            name: 'S3',
            platform: {
                id: '76b648e3-dc59-4c21-8dc7-997490052ea9',
                name: 'AWS',
            },
            result_string_template: '{bucket}/{suffix}/{path}',
            technical_info_template: '{bucket_arn}/{bucket}/{suffix}/{path}/*',
        },
        config: ['datalake', 'ingress', 'egress'],
    },
];
export const mockGetPlatformConfigs = (
    resp: GetAllPlatformServiceConfigurationsResponse = {
        platform_service_configurations: mock_platform_service_configuration,
    },
) => {
    server.use(
        http.get('*/api/v2/configuration/platforms/configs', () => {
            return HttpResponse.json(resp);
        }),
    );
};
