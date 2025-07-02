import { Flex, Typography } from 'antd';
import yaml from 'js-yaml';
import { useTranslation } from 'react-i18next';
import {
    useGetDataOutputByIdQuery,
    useGetDataOutputConfigQuery,
} from '@/store/features/data-outputs/data-outputs-api-slice';
import { useGetPlatformServiceConfigQuery } from '@/store/features/platform-service-configs/platform-service-configs-api-slice';
import type { OutputConfig } from '@/types/data-output';

type Props = {
    data_output_id: string;
};

export function DataOutputSubtitle({ data_output_id }: Props) {
    const { t } = useTranslation();
    const { data: data_output } = useGetDataOutputByIdQuery(data_output_id);
    const { data: platforms } = useGetPlatformServiceConfigQuery(
        { platformId: data_output?.platform_id || '', serviceId: data_output?.service_id || '' },
        {
            skip: !data_output,
        },
    );
    const { data: config_yaml } = useGetDataOutputConfigQuery(platforms?.service.name);
    let config: OutputConfig | undefined;
    if (config_yaml) {
        try {
            const parsed = yaml.load(config_yaml) as Record<string, OutputConfig>;
            config = parsed[Object.keys(parsed)[0]];
        } catch (_error) {
            config = undefined;
        }
    }
    if (!data_output) {
        return null;
    }

    const description = t(config?.subtitle_label || '');

    if (!description) {
        return null;
    }

    return (
        <Flex vertical>
            <Typography.Text strong>{description}: </Typography.Text>
            <Typography.Text> {data_output.result_string} </Typography.Text>
        </Flex>
    );
}
