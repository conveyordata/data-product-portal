import { Badge, Button, Popconfirm, TableColumnsType } from 'antd';
import { TFunction } from 'i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DatasetPopoverTitle } from '@/components/datasets/dataset-popover-title/dataset-popover-title';
import { DatasetTitle } from '@/components/datasets/dataset-title/dataset-title';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { DatasetLink } from '@/types/data-product';
import { createDatasetIdPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDataProductDatasetLinkBadgeStatus, getDataProductDatasetLinkStatusLabel } from '@/utils/status.helper.ts';
import { FilterSettings } from '@/utils/table-filter.helper';
import { Sorter } from '@/utils/table-sorter.helper';

import styles from './dataset-table.module.scss';

type Props = {
    t: TFunction;
    datasetLinks: DatasetLink[];
    onRemoveDataProductDatasetLink: (datasetId: string, name: string) => void;
    onCancelDataProductDatasetLinkRequest: (datasetId: string, name: string) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
};

export const getDataProductDatasetsColumns = ({
    onRemoveDataProductDatasetLink,
    onCancelDataProductDatasetLinkRequest,
    t,
    datasetLinks,
    isDisabled,
    isLoading,
}: Props): TableColumnsType<DatasetLink> => {
    const sorter = new Sorter<DatasetLink>();
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
                const isDatasetRequestApproved = status === DecisionStatus.Approved;
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
                                status={getDataProductDatasetLinkBadgeStatus(status)}
                                text={getDataProductDatasetLinkStatusLabel(t, status)}
                                className={styles.noSelect}
                            />
                        }
                    />
                );
            },
            width: '100%',
            ...new FilterSettings(datasetLinks, (datasetLink) =>
                getDataProductDatasetLinkStatusLabel(t, datasetLink.status),
            ),
            sorter: sorter.stringSorter((datasetLink) => datasetLink.dataset.name),
            defaultSortOrder: 'ascend',
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, { dataset, dataset_id, status }) => {
                const buttonText = status === DecisionStatus.Pending ? t('Cancel') : t('Remove');
                const popupTitle = status === DecisionStatus.Pending ? t('Cancel Request') : t('Unlink Dataset');
                const popupDescription =
                    status === DecisionStatus.Pending
                        ? t('Are you sure you want to cancel the request to link {{name}} to the data product?', {
                              name: dataset.name,
                          })
                        : t('Are you sure you want to remove {{name}} from the data product?', {
                              name: dataset.name,
                          });
                const onConfirm =
                    status === DecisionStatus.Pending
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
