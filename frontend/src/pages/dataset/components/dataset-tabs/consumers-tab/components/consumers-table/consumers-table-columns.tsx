import { Badge, Button, Flex, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';
import { useTranslation } from 'react-i18next';
import explorationBorderIcon from '@/assets/icons/border-icons/exploration-border-icon.svg?react';
import Justification from '@/components/data-products/data-product-dataset-justification/justification.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { InputPortReasoningButton } from '@/components/input-port-reasoning-modal/input-port-reasoning-button.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { useGetDataProductQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import {
    type AbstractDataProductInfo,
    AbstractDataProductType,
    type OutputPortInputPort,
} from '@/store/api/services/generated/dataProductsOutputPortsInputPortsApi.ts';
import { createAbstractDataProductIdPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';
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
};
type NameColumnProps = {
    status: DecisionStatus;
    consumingAbstractDataProductId: string;
    consumingAbstractDataProduct: AbstractDataProductInfo;
};
const NameColumn = ({ status, consumingAbstractDataProductId, consumingAbstractDataProduct }: NameColumnProps) => {
    const { t } = useTranslation();
    const popover = (() => {
        switch (consumingAbstractDataProduct.abstract_data_product_type) {
            case AbstractDataProductType.DataProducts:
                return t('The consumer is a Data Product named: {{name}}', { name: consumingAbstractDataProduct.name });
            case AbstractDataProductType.Explorations:
                return t('The consumer is an Exploration named: {{name}}', { name: consumingAbstractDataProduct.name });
            default:
                return undefined;
        }
    })();
    const { data: dataProduct } = useGetDataProductQuery(consumingAbstractDataProductId, {
        skip: consumingAbstractDataProduct.abstract_data_product_type !== AbstractDataProductType.DataProducts,
    });
    const icon = (() => {
        switch (consumingAbstractDataProduct.abstract_data_product_type) {
            case AbstractDataProductType.DataProducts:
                return getDataProductTypeIcon(dataProduct?.type?.icon_key);
            case AbstractDataProductType.Explorations:
                return explorationBorderIcon;
            default:
                return undefined;
        }
    })();
    return (
        <TableCellAvatar
            popover={{ title: popover }}
            linkTo={createAbstractDataProductIdPath(
                consumingAbstractDataProductId,
                consumingAbstractDataProduct.abstract_data_product_type,
            )}
            icon={<CustomSvgIconLoader iconComponent={icon} hasRoundBorder size={'default'} />}
            title={consumingAbstractDataProduct.name}
            subtitle={<Badge status={getDecisionStatusBadgeStatus(status)} text={getDecisionStatusLabel(t, status)} />}
        />
    );
};

export const getConsumerColumns = ({
    t,
    dataProductId,
    dataProductLinks,
    onRemoveDataProductDatasetLink,
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
            render: (_, { consuming_abstract_data_product, consuming_abstract_data_product_id, status }) => {
                return (
                    <NameColumn
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
            render: (_, { justification }) => <Justification justification={justification} />,
        },
        {
            title: t('Actions'),
            key: 'action',
            // hidden: !canApprove && !canRevoke,
            fixed: 'right',
            width: 1,
            render: (
                _,
                {
                    consuming_abstract_data_product: consuming_data_product,
                    consuming_abstract_data_product_id: consuming_data_product_id,
                    status,
                    id,
                    reasoning,
                },
            ) => {
                if (status === DecisionStatus.Pending && (canApprove || canRevoke)) {
                    return (
                        <Button onClick={() => setReviewingOutputPortInputPortId(id)}>
                            {t('Review Data Product Access')}
                        </Button>
                    );
                }

                if (status === DecisionStatus.Approved) {
                    return (
                        <Flex>
                            <InputPortReasoningButton reasoning={reasoning} />
                            {/*//TODO This should open a simple modal asking for reasoning*/}
                            {/*{canRevoke &&<Popconfirm*/}
                            {/*    title={t('Revoke Data Product Access')}*/}
                            {/*    description={t('Are you sure you want to revoke access from Data Product {{name}}?', {*/}
                            {/*        name: consuming_data_product.name,*/}
                            {/*    })}*/}
                            {/*    onConfirm={() =>*/}
                            {/*        onRejectDataProductDatasetLink({*/}
                            {/*            outputPortId,*/}
                            {/*            dataProductId,*/}
                            {/*            denyOutputPortAsInputPortRequest: {*/}
                            {/*                consuming_data_product_id: consuming_data_product_id,*/}
                            {/*            },*/}
                            {/*        })*/}
                            {/*    }*/}
                            {/*    placement={'leftTop'}*/}
                            {/*    okText={t('Confirm')}*/}
                            {/*    cancelText={t('Cancel')}*/}
                            {/*    okButtonProps={{ loading: isLoading }}*/}
                            {/*    autoAdjustOverflow={true}*/}
                            {/*>*/}
                            {/*    <Button loading={isLoading} disabled={isLoading || !canRevoke} type={'link'}>*/}
                            {/*        {t('Revoke Access')}*/}
                            {/*    </Button>*/}
                            {/*</Popconfirm>}*/}
                        </Flex>
                    );
                }

                if (status === DecisionStatus.Denied) {
                    return (
                        <Flex gap={'small'}>
                            <InputPortReasoningButton reasoning={reasoning} />

                            <Popconfirm
                                title={t('Remove the access request')}
                                description={t(
                                    'Are you sure you want to remove the access request from Data product {{name}}?',
                                    {
                                        name: consuming_data_product.name,
                                    },
                                )}
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
                        </Flex>
                    );
                }
            },
        },
    ];
};
