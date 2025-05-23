import { Badge, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DatasetPopoverTitle } from '@/components/datasets/dataset-popover-title/dataset-popover-title';
import { DatasetTitle } from '@/components/datasets/dataset-title/dataset-title';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { DatasetActionButton } from '@/pages/data-product/components/data-product-tabs/dataset-tab/components/dataset-table/dataset-action-button.component.tsx';
import type { DatasetLink } from '@/types/data-product';
import { createDatasetIdPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

import styles from './dataset-table.module.scss';

type Props = {
    t: TFunction;
    datasetLinks: DatasetLink[];
};
export const getDataProductDatasetsColumns = ({ t, datasetLinks }: Props): TableColumnsType<DatasetLink> => {
    const sorter = new Sorter<DatasetLink>();
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
            ...new FilterSettings(datasetLinks, (datasetLink) => getDecisionStatusLabel(t, datasetLink.status)),
            sorter: sorter.stringSorter((datasetLink) => datasetLink.dataset.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, { dataset, data_product_id, status }) => {
                return <DatasetActionButton dataset={dataset} dataProductId={data_product_id} status={status} />;
            },
        },
    ];
};
