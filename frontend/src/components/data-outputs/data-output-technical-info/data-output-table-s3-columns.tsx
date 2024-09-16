import { Badge, Button, Flex, List, Popconfirm, TableColumnsType } from 'antd';
import styles from './data-output-table.module.scss';
import { TFunction } from 'i18next';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DataOutputsGetContract } from '@/types/data-output/data-outputs-get.contract';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';
import { DataOutputSubtitle } from '@/components/data-outputs/data-output-subtitle/data-output-subtitle.component';
import { createDataOutputIdPath } from '@/types/navigation';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component';
import i18n from '@/i18n';
import { EnvironmentConfig } from '@/types/environment';
import { TechnicalInfoContract } from '@/types/data-output/data-output-technical-info.contract';
import { S3DataOutputContract } from '@/types/data-output';

type Props = {
    t: TFunction;
};

export const getS3TechnicalInformationColumns = ({
    t,
}: Props): TableColumnsType<TechnicalInfoContract> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Environment'),
            dataIndex: 'environment',
            render: (_, { environmentConfig }) => {
                return environmentConfig.environment.name
            },
            width: '30%',
        },
        {
            title: t('Path'),
            dataIndex: 'path',
            render: (_, { environmentConfig, data_output }) => {
                const configuration: S3DataOutputContract = data_output.configuration as S3DataOutputContract
                let bucket_arn = environmentConfig.config[configuration.bucket].arn

                return bucket_arn + '/' + configuration.prefix
            },
            width: '30%',
        },
    ];
};
