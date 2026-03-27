import { HttpResponse, http } from 'msw';
import {
    type PlatformTile,
    type PlatformTileResponse,
    type PluginResponse,
    UIElementType,
    type UiElementMetadataResponse,
} from '@/store/api/services/generated/pluginsApi.ts';
import { server } from '@/tests/mocks/server.ts';

export const mock_plugins: UiElementMetadataResponse[] = [
    {
        not_configured: false,
        ui_metadata: [
            {
                label: 'Bucket',
                type: UIElementType.Select,
                required: true,
                name: 'bucket',
                tooltip: null,
                hidden: null,
                checkbox: null,
                select: {
                    max_count: 1,
                    options: [
                        {
                            label: 'datalake',
                            value: 'datalake',
                        },
                        {
                            label: 'ingress',
                            value: 'ingress',
                        },
                        {
                            label: 'egress',
                            value: 'egress',
                        },
                    ],
                },
                string: null,
                radio: null,
                depends_on: null,
                disabled: null,
                use_namespace_when_not_source_aligned: null,
            },
            {
                label: 'Suffix',
                type: UIElementType.String,
                required: true,
                name: 'suffix',
                tooltip: null,
                hidden: true,
                checkbox: null,
                select: null,
                string: {
                    initial_value: '',
                },
                radio: null,
                depends_on: null,
                disabled: null,
                use_namespace_when_not_source_aligned: null,
            },
            {
                label: 'Path',
                type: UIElementType.String,
                required: true,
                name: 'path',
                tooltip: 'The name of the path to give write access to',
                hidden: null,
                checkbox: null,
                select: null,
                string: {
                    initial_value: null,
                },
                radio: null,
                depends_on: null,
                disabled: null,
                use_namespace_when_not_source_aligned: null,
            },
        ],
        plugin: 'S3TechnicalAssetConfiguration',
        has_environments: true,
        result_label: 'Resulting path',
        result_tooltip: 'The path you can access through this technical asset',
        platform: 's3',
        display_name: 'S3',
        icon_name: 's3-logo.svg',
        parent_platform: 'aws',
        platform_tile: null,
        show_in_form: true,
        detailed_name: 'Path',
    },
];

export const mockGetPlugins = (plugins: PluginResponse = { plugins: mock_plugins }) => {
    server.use(
        http.get('*/api/v2/plugins', () => {
            return HttpResponse.json(plugins);
        }),
    );
};

export const mock_platform_tiles: PlatformTile[] = [
    {
        label: 'AWS',
        value: 'aws',
        icon_name: 'aws-logo.svg',
        has_environments: true,
        has_config: true,
        children: [
            {
                label: 'Glue',
                value: 'glue',
                icon_name: 'glue-logo.svg',
                has_environments: true,
                has_config: true,
                children: [],
                show_in_form: true,
            },
            {
                label: 'S3',
                value: 's3',
                icon_name: 's3-logo.svg',
                has_environments: true,
                has_config: true,
                children: [],
                show_in_form: true,
            },
        ],
        show_in_form: true,
    },
];

export const mockGetPlatformTiles = (resp: PlatformTileResponse = { platform_tiles: mock_platform_tiles }) => {
    server.use(
        http.get('*/api/v2/plugins/platform-tiles', () => {
            return HttpResponse.json(resp);
        }),
    );
};

export const mockRenderTechnicalAssetAccessPath = (rendered_path = 'bogus') => {
    server.use(
        http.post('*/api/v2/plugins/render_technical_asset_access_path', () => {
            return HttpResponse.json({ technical_asset_access_path: rendered_path });
        }),
    );
};
