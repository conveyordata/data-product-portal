import { Badge, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DatasetPopoverTitle } from '@/components/datasets/dataset-popover-title/dataset-popover-title';
import { OutputPortTitle } from '@/components/datasets/output-port-title/output-port-title.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { DatasetActionButton } from '@/pages/data-output/components/data-output-tabs/dataset-tab/components/dataset-table/dataset-action-button.component.tsx';
import type { OutputPortLink } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';
import styles from './dataset-table.module.scss';

type Props = {
    t: TFunction;
    dataProductId: string;
};
export const getDataOutputDatasetsColumns = ({ t, dataProductId }: Props): TableColumnsType<OutputPortLink> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { output, status }) => {
                const isDatasetRequestApproved = status === DecisionStatus.Approved;
                const popoverTitle = (
                    <DatasetPopoverTitle
                        name={output.name}
                        accessType={output.access_type}
                        isApproved={isDatasetRequestApproved}
                    />
                );
                return (
                    <TableCellAvatar
                        popover={{ title: popoverTitle, content: output.description }}
                        linkTo={createMarketplaceOutputPortPath(output.id, output.data_product_id)}
                        icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                        title={<OutputPortTitle name={output.name} accessType={output.access_type} />}
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
            render: (_, { output, output_port_id, status }) => {
                return (
                    <DatasetActionButton
                        outputPort={output}
                        technicalAssetId={output_port_id}
                        dataProductId={dataProductId}
                        status={status}
                    />
                );
            },
        },
    ];
};
