import { Badge, Button, Popconfirm, TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DatasetPopoverTitle } from '@/components/datasets/dataset-popover-title/dataset-popover-title';
import { DatasetTitle } from '@/components/datasets/dataset-title/dataset-title';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import type { DataOutputDatasetLink } from '@/types/data-output';
import { createDatasetIdPath } from '@/types/navigation.ts';
import { getDataOutputDatasetLinkBadgeStatus, getDataOutputDatasetLinkStatusLabel } from '@/utils/status.helper.ts';

import styles from './dataset-table.module.scss';

type Props = {
    t: TFunction;
    onRemoveDataOutputDatasetLink: (datasetId: string, name: string) => void;
    onCancelDataOutputDatasetLinkRequest: (datasetId: string, name: string) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
};

export const getDataOutputDatasetsColumns = ({
    onRemoveDataOutputDatasetLink,
    onCancelDataOutputDatasetLinkRequest,
    t,
    isDisabled,
    isLoading,
}: Props): TableColumnsType<DataOutputDatasetLink> => {
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
                const isDatasetRequestApproved = status === 'approved';
                const popoverTitle = (
                    <DatasetPopoverTitle
                        name={dataset.name}
                        accessType={dataset.access_type}
                        isApproved={isDatasetRequestApproved}
                    />
                );
                return (
                    <TableCellAvatar
                        popover={{ title: popoverTitle, content: dataset.description }}
                        linkTo={createDatasetIdPath(dataset.id)}
                        icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                        title={<DatasetTitle name={dataset.name} accessType={dataset.access_type} />}
                        subtitle={
                            <Badge
                                status={getDataOutputDatasetLinkBadgeStatus(status)}
                                text={getDataOutputDatasetLinkStatusLabel(t, status)}
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
                const popupTitle = status === 'pending_approval' ? t('Cancel Request') : t('Unlink Dataset');
                const popupDescription =
                    status === 'pending_approval'
                        ? t('Are you sure you want to cancel the request to link {{name}} to the data output?', {
                              name: dataset.name,
                          })
                        : t('Are you sure you want to remove {{name}} from the data output?', {
                              name: dataset.name,
                          });
                const onConfirm =
                    status === 'pending_approval'
                        ? onCancelDataOutputDatasetLinkRequest
                        : onRemoveDataOutputDatasetLink;
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
