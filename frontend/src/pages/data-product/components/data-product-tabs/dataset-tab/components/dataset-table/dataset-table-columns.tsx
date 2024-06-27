import { Badge, Button, Popconfirm, TableColumnsType } from 'antd';
import { getDataProductDatasetLinkBadgeStatus, getDataProductDatasetLinkStatusLabel } from '@/utils/status.helper.ts';
import styles from './dataset-table.module.scss';
import { TFunction } from 'i18next';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { createDatasetIdPath } from '@/types/navigation.ts';
import { DatasetLink } from '@/types/data-product';
import { RestrictedDatasetPopoverTitle } from '@/components/datasets/restricted-dataset-popover-title/restricted-dataset-popover-title.tsx';
import { RestrictedDatasetTitle } from '@/components/datasets/restricted-dataset-title/restricted-dataset-title.tsx';

type Props = {
    t: TFunction;
    onRemoveDataProductDatasetLink: (datasetId: string, name: string) => void;
    onCancelDataProductDatasetLinkRequest: (datasetId: string, name: string) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
};

export const getDataProductDatasetsColumns = ({
    onRemoveDataProductDatasetLink,
    onCancelDataProductDatasetLinkRequest,
    t,
    isDisabled,
    isLoading,
}: Props): TableColumnsType<DatasetLink> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { dataset, status }) => {
                const isRestrictedDataset = dataset.access_type === 'restricted';
                const isDatasetRequestApproved = status === 'approved';
                const popoverTitle = isRestrictedDataset ? (
                    <RestrictedDatasetPopoverTitle name={dataset.name} isApproved={isDatasetRequestApproved} />
                ) : (
                    dataset.name
                );
                const title = isRestrictedDataset ? <RestrictedDatasetTitle name={dataset.name} /> : dataset.name;
                return (
                    <TableCellAvatar
                        popover={{ title: popoverTitle, content: dataset.description }}
                        linkTo={createDatasetIdPath(dataset.id)}
                        icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                        title={title}
                        subtitle={
                            <Badge
                                status={getDataProductDatasetLinkBadgeStatus(status)}
                                text={getDataProductDatasetLinkStatusLabel(status)}
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
            render: (_, { dataset, dataset_id, status }) => {
                const buttonText = status === 'pending_approval' ? t('Cancel') : t('Remove');
                const popupTitle = status === 'pending_approval' ? t('Cancel Request') : t('Remove Dataset');
                const popupDescription =
                    status === 'pending_approval'
                        ? t('Are you sure you want to cancel the request to link {{name}} to the data product?', {
                              name: dataset.name,
                          })
                        : t('Are you sure you want to remove {{name}} from the data product?', {
                              name: dataset.name,
                          });
                const onConfirm =
                    status === 'pending_approval'
                        ? onCancelDataProductDatasetLinkRequest
                        : onRemoveDataProductDatasetLink;
                return (
                    <Popconfirm
                        title={popupTitle}
                        description={popupDescription}
                        onConfirm={() => onConfirm(dataset_id, dataset.name)}
                        placement={'leftTop'}
                        okText={t('Confirm')}
                        cancelText={t('Cancel')}
                        okButtonProps={{ loading: isLoading }}
                        autoAdjustOverflow={true}
                    >
                        <Button loading={isLoading} disabled={isLoading || isDisabled} type={'link'}>
                            {buttonText}
                        </Button>
                    </Popconfirm>
                );
            },
        },
    ];
};
