import { Badge, Flex, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import outputPortBorderIcon from '@/assets/icons/border-icons/output-port-border-icon.svg?react';
import { InputPortActionButton } from '@/components/abstract-data-products/input-port-tab/components/input-port-table/input-port-action-botton.component.tsx';
import { DatasetPopoverTitle } from '@/components/datasets/dataset-popover-title/dataset-popover-title.tsx';
import { OutputPortTitle } from '@/components/datasets/output-port-title/output-port-title.tsx';
import EllipsisParagraph from '@/components/ellipsis-paragraph/ellipsis-paragraph.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { ExpiryDate, IsExpiringSoonTag, RenewalTag } from '@/components/input-port/access-status.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import {
    type AbstractDataProductInputPort as InputPort,
    InputPortStatus,
} from '@/store/api/services/generated/dataProductsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { getInputPortStatusBadgeStatus, getInputPortStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper.ts';
import { Sorter } from '@/utils/table-sorter.helper.ts';

type Props = {
    t: TFunction;
    canRemoveAccess: boolean;
    canRequestAccess: boolean;
    handleRemove: (outputPortId: string) => Promise<void>;
    handleRenew: (outputPortId: string) => Promise<void>;
    inputPorts: InputPort[];
};
export const getDataProductDatasetsColumns = ({
    t,
    canRemoveAccess,
    canRequestAccess,
    handleRemove,
    handleRenew,
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
            width: '22%',
            render: (_, { output_port, status }) => {
                const isDatasetRequestApproved = status === InputPortStatus.Approved;
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
            sorter: sorter.stringSorter((input_port) => input_port.output_port.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            width: '18%',
            render: (_, { status, renewal_status }) => (
                <Flex vertical align={'flex-start'} gap={'small'}>
                    <Badge status={getInputPortStatusBadgeStatus(status)} text={getInputPortStatusLabel(t, status)} />
                    <RenewalTag status={status} renewalStatus={renewal_status} />
                </Flex>
            ),
            ...new FilterSettings(inputPorts, (input_port) => getInputPortStatusLabel(t, input_port.status)),
            sorter: sorter.stringSorter((input_port) => getInputPortStatusLabel(t, input_port.status)),
        },
        {
            title: t('Business justification'),
            dataIndex: ['current_request', 'justification'],
            width: '30%',
            render: (_, { current_request }) => <EllipsisParagraph text={current_request.justification} />,
        },
        {
            title: t('Expiry date'),
            dataIndex: ['current_request', 'valid_until'],
            width: '12%',
            render: (_, { status, renewal_status, current_request }) => (
                <Flex vertical align={'flex-start'} gap={'small'}>
                    <ExpiryDate status={status} validUntil={current_request.valid_until} />
                    <IsExpiringSoonTag
                        status={status}
                        validUntil={current_request.valid_until}
                        renewalStatus={renewal_status}
                    />
                </Flex>
            ),
        },
        {
            title: t('Decision note'),
            dataIndex: ['current_request', 'decision_note'],
            render: (_, { current_request }) => <EllipsisParagraph text={current_request.decision_note} />,
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, { output_port, status, current_request, renewal_status }) => {
                return (
                    <InputPortActionButton
                        output_port={output_port}
                        canRemoveAccess={canRemoveAccess}
                        canRequestAccess={canRequestAccess}
                        handleRemove={handleRemove}
                        handleRenew={handleRenew}
                        status={status}
                        validUntil={current_request.valid_until}
                        renewalStatus={renewal_status}
                    />
                );
            },
            fixed: 'right',
            width: 1,
        },
    ];
};
