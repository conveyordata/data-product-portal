import { Button, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';
import EllipsisParagraph from '@/components/ellipsis-paragraph/ellipsis-paragraph.component.tsx';
import { ConsumerColumn } from '@/components/input-port/consumer-column.tsx';
import type { OutputPortInputPort } from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusLabel } from '@/utils/status.helper.ts';
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
            render: (_, { consuming_abstract_data_product, consuming_abstract_data_product_id, status }) => {
                return (
                    <ConsumerColumn
                        status={status}
                        consumingAbstractDataProductId={consuming_abstract_data_product_id}
                        consumingAbstractDataProduct={consuming_abstract_data_product}
                    />
                );
            },
            width: '25%',
            ...new FilterSettings(dataProductLinks, (dpl) => getDecisionStatusLabel(t, dpl.status)),
            sorter: sorter.stringSorter((dpl) => dpl.consuming_abstract_data_product.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Business justification'),
            dataIndex: 'justification',
            render: (_, { justification }) => <EllipsisParagraph text={justification} />,
        },
        {
            title: t('Decision note'),
            dataIndex: 'decision_note',
            render: (_, { decision_note: decisionNote }) => <EllipsisParagraph text={decisionNote} />,
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
                if (status === DecisionStatus.Pending && (canApprove || canRevoke)) {
                    return (
                        <Button type={'link'} onClick={() => setReviewingOutputPortInputPortId(id)}>
                            {t('Review Access Request')}
                        </Button>
                    );
                }

                if (status === DecisionStatus.Approved) {
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

                if (status === DecisionStatus.Denied) {
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
