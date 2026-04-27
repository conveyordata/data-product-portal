import { Badge, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import Justification from '@/components/data-products/data-product-dataset-justification/justification.component.tsx';
import { DatasetPopoverTitle } from '@/components/datasets/dataset-popover-title/dataset-popover-title';
import { OutputPortTitle } from '@/components/datasets/output-port-title/output-port-title.tsx';
import { FreshnessBadge } from '@/components/freshness-badge/freshness-badge.component';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { InputPortActionButton } from '@/pages/data-product/components/data-product-tabs/input-port-tab/components/input-port-table/input-port-action-botton.component.tsx';
import type { InputPort } from '@/store/api/services/generated/dataProductsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    dataProductId: string;
    inputPorts: InputPort[];
};
export const getDataProductDatasetsColumns = ({ t, dataProductId, inputPorts }: Props): TableColumnsType<InputPort> => {
    const sorter = new Sorter<InputPort>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { output_port, status }) => {
                const isDatasetRequestApproved = status === DecisionStatus.Approved;
                const popoverTitle = (
                    <DatasetPopoverTitle
                        name={output_port.name}
                        accessType={output_port.access_type}
                        isApproved={isDatasetRequestApproved}
                    />
                );
                return (
                    <TableCellAvatar
                        popover={{ title: popoverTitle, content: output_port.description }}
                        linkTo={createMarketplaceOutputPortPath(output_port.id, output_port.data_product_id)}
                        icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                        title={<OutputPortTitle name={output_port.name} accessType={output_port.access_type} />}
                        subtitle={
                            <Badge
                                status={getDecisionStatusBadgeStatus(status)}
                                text={getDecisionStatusLabel(t, status)}
                            />
                        }
                    />
                );
            },
            width: '25%',
            ...new FilterSettings(inputPorts, (input_port) => getDecisionStatusLabel(t, input_port.status)),
            sorter: sorter.stringSorter((input_port) => input_port.output_port.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Business justification'),
            dataIndex: 'justification',
            render: (_, { justification }) => <Justification justification={justification} />,
        },
        {
            title: t('Freshness'),
            key: 'freshness',
            render: (_, { output_port }) => {
                if (!output_port.freshness_status) return null;
                return (
                    <FreshnessBadge
                        status={output_port.freshness_status}
                        deadlineTime={output_port.freshness_deadline_time}
                    />
                );
            },
            width: '15%',
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, { output_port, status }) => {
                return (
                    <InputPortActionButton output_port={output_port} dataProductId={dataProductId} status={status} />
                );
            },
            fixed: 'right',
            width: 1,
        },
    ];
};
