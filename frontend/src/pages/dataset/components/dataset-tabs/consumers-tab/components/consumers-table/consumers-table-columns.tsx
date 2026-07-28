import { CloseCircleOutlined, EyeOutlined } from '@ant-design/icons';
import { Badge, Button, Flex, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';
import EllipsisParagraph from '@/components/ellipsis-paragraph/ellipsis-paragraph.component.tsx';
import { ExpiryDate, IsExpiringSoonTag, RenewalTag } from '@/components/input-port/access-status.tsx';
import { ConsumerColumn } from '@/components/input-port/consumer-column.tsx';
import {
    InputPortStatus,
    type OutputPortInputPort,
    RenewalStatus,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { getInputPortStatusBadgeStatus, getInputPortStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    outputPortId: string;
    dataProductLinks: OutputPortInputPort[];
    onRevokeDataProductDatasetLink: (name: string, consumingDataProductId: string) => void;
    isLoading?: boolean;
    canApprove?: boolean;
    canRevoke?: boolean;
    setReviewingOutputPortInputPortId: (id: string) => void;
};

export const getConsumerColumns = ({
    t,
    dataProductLinks,
    onRevokeDataProductDatasetLink,
    canApprove,
    canRevoke,
    setReviewingOutputPortInputPortId,
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
                <Flex vertical align={'flex-start'} gap={'small'}>
                    <Badge status={getInputPortStatusBadgeStatus(status)} text={getInputPortStatusLabel(t, status)} />
                    <RenewalTag renewalStatus={renewal_status} />
                    <IsExpiringSoonTag
                        status={status}
                        validUntil={current_request.valid_until}
                        renewalStatus={renewal_status}
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
                    renewal_status,
                    id,
                },
            ) => {
                const showReview =
                    (status === InputPortStatus.Pending || renewal_status === RenewalStatus.Pending) &&
                    (canApprove || canRevoke);
                const showRevoke = status === InputPortStatus.Approved;

                return (
                    <Flex gap={'small'} wrap>
                        {showReview && (
                            <Button
                                icon={<EyeOutlined />}
                                type={'link'}
                                onClick={() => setReviewingOutputPortInputPortId(id)}
                            >
                                {t('Review Access Request')}
                            </Button>
                        )}
                        {showRevoke && (
                            <Popconfirm
                                title={t('Revoke Access')}
                                description={t('Are you sure you want to revoke access for {{name}}?', {
                                    name: consuming_data_product.name,
                                })}
                                onConfirm={() =>
                                    onRevokeDataProductDatasetLink(
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
                                    icon={<CloseCircleOutlined />}
                                    type={'link'}
                                    loading={isLoading}
                                    disabled={isLoading || !canRevoke}
                                >
                                    {t('Revoke Access')}
                                </Button>
                            </Popconfirm>
                        )}
                    </Flex>
                );
            },
        },
    ];
};
