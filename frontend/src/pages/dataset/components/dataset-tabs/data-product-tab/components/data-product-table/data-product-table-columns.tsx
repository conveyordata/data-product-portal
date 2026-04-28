import { Badge, Button, Flex, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';
import chipIcon from '@/assets/icons/chip-icon.svg?react';
import Justification from '@/components/data-products/data-product-dataset-justification/justification.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import type {
    ApproveOutputPortAsInputPortApiArg,
    DenyOutputPortAsInputPortApiArg,
    OutputPortInputPort,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { createDataProductIdPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

type Props = {
    t: TFunction;
    dataProductId: string;
    outputPortId: string;
    dataProductLinks: OutputPortInputPort[];
    onAcceptDataProductDatasetLink: (request: ApproveOutputPortAsInputPortApiArg) => void;
    onRejectDataProductDatasetLink: (request: DenyOutputPortAsInputPortApiArg) => void;
    onRemoveDataProductDatasetLink: (data_productId: string, name: string, consumingDataProductId: string) => void;
    isLoading?: boolean;
    canApprove?: boolean;
    canRevoke?: boolean;
};

export const getDatasetDataProductsColumns = ({
    t,
    dataProductId,
    outputPortId,
    dataProductLinks,
    onRemoveDataProductDatasetLink,
    onRejectDataProductDatasetLink,
    onAcceptDataProductDatasetLink,
    isLoading,
    canApprove,
    canRevoke,
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
                    <TableCellAvatar
                        popover={{ title: consuming_abstract_data_product.name }}
                        linkTo={createDataProductIdPath(consuming_abstract_data_product_id)}
                        icon={<CustomSvgIconLoader iconComponent={chipIcon} hasRoundBorder size={'default'} />}
                        title={consuming_abstract_data_product.name}
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
            ...new FilterSettings(dataProductLinks, (dpl) => getDecisionStatusLabel(t, dpl.status)),
            sorter: sorter.stringSorter((dpl) => dpl.consuming_abstract_data_product.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Business justification'),
            dataIndex: 'justification',
            render: (_, { justification }) => <Justification justification={justification} />,
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
                },
            ) => {
                if (status === DecisionStatus.Pending) {
                    return (
                        <Flex>
                            <Popconfirm
                                title={t('Allow Data Product Access')}
                                description={t('Are you sure you want to allow access to Data Product {{name}}?', {
                                    name: consuming_data_product.name,
                                })}
                                onConfirm={() =>
                                    onAcceptDataProductDatasetLink({
                                        outputPortId,
                                        dataProductId,
                                        approveOutputPortAsInputPortRequest: {
                                            consuming_data_product_id: consuming_data_product_id,
                                        },
                                    })
                                }
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button loading={isLoading} disabled={isLoading || !canApprove} type={'link'}>
                                    {t('Accept')}
                                </Button>
                            </Popconfirm>
                            <Popconfirm
                                title={t('Deny Data Product Access')}
                                description={t('Are you sure you want to deny access to Data Product {{name}}?', {
                                    name: consuming_data_product.name,
                                })}
                                onConfirm={() =>
                                    onRejectDataProductDatasetLink({
                                        outputPortId,
                                        dataProductId,
                                        denyOutputPortAsInputPortRequest: {
                                            consuming_data_product_id: consuming_data_product_id,
                                        },
                                    })
                                }
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button loading={isLoading} disabled={isLoading || !canApprove} type={'link'}>
                                    {t('Reject')}
                                </Button>
                            </Popconfirm>
                        </Flex>
                    );
                }
                if (status === DecisionStatus.Approved) {
                    return (
                        <Popconfirm
                            title={t('Revoke Data Product Access')}
                            description={t('Are you sure you want to revoke access from Data Product {{name}}?', {
                                name: consuming_data_product.name,
                            })}
                            onConfirm={() =>
                                onRejectDataProductDatasetLink({
                                    outputPortId,
                                    dataProductId,
                                    denyOutputPortAsInputPortRequest: {
                                        consuming_data_product_id: consuming_data_product_id,
                                    },
                                })
                            }
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: isLoading }}
                            autoAdjustOverflow={true}
                        >
                            <Button loading={isLoading} disabled={isLoading || !canRevoke} type={'link'}>
                                {t('Revoke Access')}
                            </Button>
                        </Popconfirm>
                    );
                }

                if (status === DecisionStatus.Denied) {
                    return (
                        <Button
                            type={'link'}
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
                    );
                }
            },
        },
    ];
};
