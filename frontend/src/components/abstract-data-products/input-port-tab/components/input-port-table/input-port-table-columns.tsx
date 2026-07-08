import { Badge, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import outputPortBorderIcon from '@/assets/icons/border-icons/output-port-border-icon.svg?react';
import { InputPortActionButton } from '@/components/abstract-data-products/input-port-tab/components/input-port-table/input-port-action-botton.component.tsx';
import Justification from '@/components/data-products/data-product-dataset-justification/justification.component.tsx';
import AccessExpiryStatus from '@/components/datasets/access-expiry-status/access-expiry-status.component.tsx';
import { DatasetPopoverTitle } from '@/components/datasets/dataset-popover-title/dataset-popover-title.tsx';
import { OutputPortTitle } from '@/components/datasets/output-port-title/output-port-title.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import type { InputPort } from '@/store/api/services/generated/dataProductsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

type Props = {
    t: TFunction;
    canRemoveAccess: boolean;
    handleRemove: (outputPortId: string) => Promise<void>;
    inputPorts: InputPort[];
};
export const getDataProductDatasetsColumns = ({
    t,
    canRemoveAccess,
    handleRemove,
    inputPorts,
}: Props): TableColumnsType<InputPort> => {
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
                        icon={<CustomSvgIconLoader iconComponent={outputPortBorderIcon} />}
                        title={<OutputPortTitle name={output_port.name} accessType={output_port.access_type} />}
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
            width: '40%',
            render: (_, { justification }) => <Justification justification={justification} />,
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            render: (_, { status }) => (
                <Badge status={getDecisionStatusBadgeStatus(status)} text={getDecisionStatusLabel(t, status)} />
            ),
        },
        {
            title: t('Access Expires'),
            dataIndex: 'expires_on',
            render: (_, { expires_on, is_expiring_soon, status }) => (
                <AccessExpiryStatus expiresOn={expires_on} isExpiringSoon={is_expiring_soon} status={status} />
            ),
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, { output_port, status }) => {
                return (
                    <InputPortActionButton
                        output_port={output_port}
                        canRemoveAccess={canRemoveAccess}
                        handleRemove={handleRemove}
                        status={status}
                    />
                );
            },
            fixed: 'right',
            width: 1,
        },
    ];
};
