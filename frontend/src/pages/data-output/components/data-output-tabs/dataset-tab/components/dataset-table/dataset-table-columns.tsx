import { Badge, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DatasetPopoverTitle } from '@/components/datasets/dataset-popover-title/dataset-popover-title';
import { DatasetTitle } from '@/components/datasets/dataset-title/dataset-title';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { DatasetActionButton } from '@/pages/data-output/components/data-output-tabs/dataset-tab/components/dataset-table/dataset-action-button.component.tsx';
import type { DataOutputDatasetLink } from '@/types/data-output';
import { createDatasetIdPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';

import styles from './dataset-table.module.scss';

type Props = {
    t: TFunction;
    dataProductId: string | undefined;
};
export const getDataOutputDatasetsColumns = ({ t, dataProductId }: Props): TableColumnsType<DataOutputDatasetLink> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { dataset, status }) => {
                const isDatasetRequestApproved = status === DecisionStatus.Approved;
                const popoverTitle = (
                    <DatasetPopoverTitle
                        name={dataset.name}
                        accessType={dataset.access_type}
                        isApproved={isDatasetRequestApproved}
                    />
                );
                return (
                    <TableCellAvatar
                        popover={{ title: popoverTitle, content: dataset.description }}
                        linkTo={createDatasetIdPath(dataset.id)}
                        icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                        title={<DatasetTitle name={dataset.name} accessType={dataset.access_type} />}
                        subtitle={
                            <Badge
                                status={getDecisionStatusBadgeStatus(status)}
                                text={getDecisionStatusLabel(t, status)}
                                className={styles.noSelect}
                            />
                        }
                    />
                );
            },
            width: '100%',
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, { dataset, data_output_id, status }) => {
                return (
                    <DatasetActionButton
                        dataset={dataset}
                        dataOutputId={data_output_id}
                        dataProductId={dataProductId}
                        status={status}
                    />
                );
            },
        },
    ];
};
