import { Badge, Button, Flex, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';
import EllipsisParagraph from '@/components/ellipsis-paragraph/ellipsis-paragraph.component.tsx';
import { ExpiryDate, RenewalTag } from '@/components/input-port/access-status.tsx';
import { ConsumerColumn } from '@/components/input-port/consumer-column.tsx';
import {
    InputPortStatus,
    type OutputPortInputPort,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { getInputPortStatusBadgeStatus, getInputPortStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    dataProductId: string;
    outputPortId: string;
    dataProductLinks: OutputPortInputPort[];
    onRemoveDataProductDatasetLink: (data_productId: string, name: string, consumingDataProductId: string) => void;
    isLoading?: boolean;
    canApprove?: boolean;
    canRevoke?: boolean;
    setReviewingOutputPortInputPortId: (id: string) => void;
    setRejectingOutputPortInputPortId: (id: string) => void;
};

export const getConsumerColumns = ({
    t,
    dataProductId,
    dataProductLinks,
    onRemoveDataProductDatasetLink,
    canApprove,
    canRevoke,
    setReviewingOutputPortInputPortId,
    setRejectingOutputPortInputPortId,
    isLoading,
}: Props): TableColumnsType<OutputPortInputPort> => {
    const sorter = new Sorter<OutputPortInputPort>();
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
            render: (_, { consuming_abstract_data_product, consuming_abstract_data_product_id }) => {
                return (
                    <ConsumerColumn
                        consumingAbstractDataProductId={consuming_abstract_data_product_id}
                        consumingAbstractDataProduct={consuming_abstract_data_product}
                    />
                );
            },
            sorter: sorter.stringSorter((dpl) => dpl.consuming_abstract_data_product.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            width: '18%',
            render: (_, { status, renewal_status, current_request }) => (
                <Flex align={'center'} gap={'small'} wrap>
                    <Badge status={getInputPortStatusBadgeStatus(status)} text={getInputPortStatusLabel(t, status)} />
                    <RenewalTag
                        status={status}
                        renewalStatus={renewal_status}
                        validUntil={current_request.valid_until}
                    />
                </Flex>
            ),
            ...new FilterSettings(dataProductLinks, (dpl) => getInputPortStatusLabel(t, dpl.status)),
            sorter: sorter.stringSorter((dpl) => getInputPortStatusLabel(t, dpl.status)),
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
            render: (_, { status, current_request }) => (
                <ExpiryDate status={status} validUntil={current_request.valid_until} />
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
            hidden: !canApprove && !canRevoke,
            fixed: 'right',
            width: 1,
            render: (
                _,
                {
                    consuming_abstract_data_product: consuming_data_product,
                    consuming_abstract_data_product_id: consuming_data_product_id,
                    status,
                    id,
                },
            ) => {
                if (status === InputPortStatus.Pending && (canApprove || canRevoke)) {
                    return (
                        <Button type={'link'} onClick={() => setReviewingOutputPortInputPortId(id)}>
                            {t('Review Access Request')}
                        </Button>
                    );
                }

                if (status === InputPortStatus.Approved) {
                    return (
                        <Button
                            type={'link'}
                            loading={isLoading}
                            disabled={isLoading || !canRevoke}
                            onClick={() => setRejectingOutputPortInputPortId(id)}
                        >
                            {t('Revoke Access')}
                        </Button>
                    );
                }

                if (status === InputPortStatus.Denied) {
                    return (
                        <Popconfirm
                            title={t('Remove the access request')}
                            description={t('Are you sure you want to remove the access request of {{name}}?', {
                                name: consuming_data_product.name,
                            })}
                            onConfirm={() =>
                                onRemoveDataProductDatasetLink(
                                    dataProductId,
                                    consuming_data_product.name,
                                    consuming_data_product_id,
                                )
                            }
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: isLoading }}
                            autoAdjustOverflow={true}
                        >
                            <Button
                                type={'link'}
                                danger
                                onClick={() =>
                                    onRemoveDataProductDatasetLink(
                                        dataProductId,
                                        consuming_data_product.name,
                                        consuming_data_product_id,
                                    )
                                }
                            >
                                {t('Remove')}
                            </Button>
                        </Popconfirm>
                    );
                }
            },
        },
    ];
};
