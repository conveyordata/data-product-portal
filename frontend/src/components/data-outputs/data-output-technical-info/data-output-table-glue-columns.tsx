
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
import { GlueDataOutputContract, S3DataOutputContract } from '@/types/data-output';

type Props = {
    t: TFunction;
};

export const getGlueTechnicalInformationColumns = ({
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
            title: t('Database'),
            dataIndex: 'database',
            render: (_, { environmentConfig, data_output }) => {
                const configuration: GlueDataOutputContract = data_output.configuration as GlueDataOutputContract
                // TODO figure out how to use product aligned databases here and get their ARN?
                return configuration.glue_database
            },
            width: '30%',
        },
    ];
};
