import { Badge, Button, Flex, Popconfirm, TableColumnsType } from 'antd';
import { getDataProductDatasetLinkBadgeStatus, getDataProductDatasetLinkStatusLabel } from '@/utils/status.helper.ts';
import styles from './data-product-table.module.scss';
import { TFunction } from 'i18next';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { createDataProductIdPath } from '@/types/navigation.ts';
import { DataProductLink } from '@/types/dataset';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper.ts';
import { DataProductDatasetLinkRequest, DataProductDatasetLinkStatus } from '@/types/data-product-dataset';
import { Sorter } from '@/utils/table-sorter.helper';
import { FilterSettings } from '@/utils/table-filter.helper';

type Props = {
    t: TFunction;
    dataProductLinks: DataProductLink[];
    onRemoveDataProductDatasetLink: (data_productId: string, name: string, datasetLinkId: string) => void;
    onAcceptDataProductDatasetLink: (request: DataProductDatasetLinkRequest) => void;
    onRejectDataProductDatasetLink: (request: DataProductDatasetLinkRequest) => void;
    isCurrentDatasetOwner: boolean;
    isLoading?: boolean;
    isDisabled?: boolean;
};

export const getDatasetDataProductsColumns = ({
    onRemoveDataProductDatasetLink,
    onRejectDataProductDatasetLink,
    onAcceptDataProductDatasetLink,
    t,
    dataProductLinks,
    isDisabled,
    isLoading,
    isCurrentDatasetOwner,
}: Props): TableColumnsType<DataProductLink> => {
    const sorter = new Sorter<DataProductLink>();
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { data_product, status }) => {
                return (
                    <TableCellAvatar
                        popover={{ title: data_product.name, content: data_product.description }}
                        linkTo={createDataProductIdPath(data_product.id)}
                        icon={
                            <CustomSvgIconLoader
                                iconComponent={getDataProductTypeIcon(data_product?.type?.icon_key)}
                                hasRoundBorder
                                size={'default'}
                            />
                        }
                        title={data_product.name}
                        subtitle={
                            <Badge
                                status={getDataProductDatasetLinkBadgeStatus(status)}
                                text={getDataProductDatasetLinkStatusLabel(t, status)}
                                className={styles.noSelect}
                            />
                        }
                    />
                );
            },
            width: '100%',
            ...new FilterSettings(dataProductLinks, (dpl) => getDataProductDatasetLinkStatusLabel(t, dpl.status)),
            sorter: sorter.stringSorter((dpl) => dpl.data_product.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Actions'),
            key: 'action',
            hidden: !isCurrentDatasetOwner,
            render: (_, { id, data_product, status, dataset_id, data_product_id }) => {
                if (status === DataProductDatasetLinkStatus.Pending) {
                    return (
                        <Flex>
                            <Popconfirm
                                title={t('Allow Data Product Access')}
                                description={t('Are you sure you want to allow access to data product {{name}}?', {
                                    name: data_product.name,
                                })}
                                onConfirm={() => onAcceptDataProductDatasetLink({ dataset_id, data_product_id, id })}
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button loading={isLoading} disabled={isLoading || isDisabled} type={'link'}>
                                    {t('Accept')}
                                </Button>
                            </Popconfirm>
                            <Popconfirm
                                title={t('Deny Data Product Access')}
                                description={t('Are you sure you want to deny access to data product {{name}}?', {
                                    name: data_product.name,
                                })}
                                onConfirm={() => onRejectDataProductDatasetLink({ dataset_id, data_product_id, id })}
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button loading={isLoading} disabled={isLoading || isDisabled} type={'link'}>
                                    {t('Reject')}
                                </Button>
                            </Popconfirm>
                        </Flex>
                    );
                }
                if (status === DataProductDatasetLinkStatus.Approved) {
                    return (
                        <Popconfirm
                            title={t('Revoke Data Product Access')}
                            description={t('Are you sure you want to revoke access from data product {{name}}?', {
                                name: data_product.name,
                            })}
                            onConfirm={() => onRejectDataProductDatasetLink({ dataset_id, data_product_id, id })}
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: isLoading }}
                            autoAdjustOverflow={true}
                        >
                            <Button loading={isLoading} disabled={isLoading || isDisabled} type={'link'}>
                                {t('Revoke Access')}
                            </Button>
                        </Popconfirm>
                    );
                }

                if (status === DataProductDatasetLinkStatus.Denied) {
                    return (
                        <Button
                            type={'link'}
                            onClick={() => onRemoveDataProductDatasetLink(data_product.id, data_product.name, id)}
                        >
                            {t('Remove')}
                        </Button>
                    );
                }
            },
        },
    ];
};
