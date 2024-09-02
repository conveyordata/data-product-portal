import { Badge, Button, Flex, List, Popconfirm, TableColumnsType } from 'antd';
import styles from './data-output-table.module.scss';
import { TFunction } from 'i18next';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DataOutputsGetContract } from '@/types/data-output/data-outputs-get.contract';
import { getDataOutputIcon } from '@/utils/data-output-type-icon.helper';
import { DataOutputSubtitle } from '@/components/data-outputs/data-output-subtitle/data-output-subtitle.component';
import { DataOutputDatasetLink } from '@/types/data-output/dataset-link.contract';
import { RestrictedDatasetPopoverTitle } from '@/components/datasets/restricted-dataset-popover-title/restricted-dataset-popover-title';
import { RestrictedDatasetTitle } from '@/components/datasets/restricted-dataset-title/restricted-dataset-title';
import { createDatasetIdPath } from '@/types/navigation';
import { getBadgeStatus, getDataOutputDatasetLinkBadgeStatus, getDataOutputDatasetLinkStatusLabel, getStatusLabel } from '@/utils/status.helper';

type Props = {
    t: TFunction;
    isLoading?: boolean;
    isDisabled?: boolean;
    handleOpen: (id: string) => void;
    onRemoveDataOutput: (id: string, name: string) => void;
    onRemoveDatasetFromDataOutput: (datasetId: string, dataOutputId: string, name: string) => void;
};

export const getDataProductDataOutputsColumns = ({
    t,
    handleOpen,
    isDisabled,
    isLoading,
    onRemoveDataOutput,
    onRemoveDatasetFromDataOutput,
}: Props): TableColumnsType<DataOutputsGetContract[0]> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { id, name, status, description, configuration_type }) => {
                return (
                    <TableCellAvatar
                        popover={{ title: name, content: description }}
                        //linkTo={createDataOutputIdPath(external_id)}
                        icon={<CustomSvgIconLoader iconComponent={getDataOutputIcon(configuration_type)!} />}
                        title={name}
                        subtitle={
                            <Flex vertical>
                             <Badge
                                     status={getBadgeStatus(status)}
                               text={getStatusLabel(status)}
                                 className={styles.noSelect}
                             />
                            <DataOutputSubtitle data_output_id={id} />
                            </Flex>
                        }
                    />
                );
            },
            width: '50%',
        },
        {
            title: t('Datasets'),
            dataIndex: 'links',
            render: (_, { dataset_links, id, name }) => {
                return (
                    <List
                        //loading={isLoading || isFetchingUsers}
                        size={'large'}
                        locale={{ emptyText: t('No datasets linked') }}
                        rowKey={(dataset_link: DataOutputDatasetLink) => dataset_link.dataset_id}
                        dataSource={dataset_links}
                        renderItem={(dataset_link) => {
                            const isRestrictedDataset = dataset_link.dataset.access_type === 'restricted';
                            const isDatasetRequestApproved = status === 'approved';
                            const popoverTitle = isRestrictedDataset ? (
                                <RestrictedDatasetPopoverTitle
                                    name={dataset_link.dataset.name}
                                    isApproved={isDatasetRequestApproved}
                                />
                            ) : (
                                dataset_link.dataset.name
                            );
                            const title = isRestrictedDataset ? (
                                <RestrictedDatasetTitle name={dataset_link.dataset.name} />
                            ) : (
                                dataset_link.dataset.name
                            );
                            return (
                                <List.Item key={dataset_link.dataset_id}>
                                    <TableCellAvatar
                                        popover={{ title: popoverTitle, content: dataset_link.dataset.description }}
                                        linkTo={createDatasetIdPath(dataset_link.dataset.id)}
                                        icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                                        title={title}
                                        subtitle={
                                            <Badge
                                                status={getDataOutputDatasetLinkBadgeStatus(dataset_link.status)}
                                                text={getDataOutputDatasetLinkStatusLabel(dataset_link.status)}
                                                className={styles.noSelect}
                                            />
                                        }
                                    />
                                    <Button
                                        onClick={() => {
                                            onRemoveDatasetFromDataOutput(dataset_link.dataset_id, id, name);
                                        }}
                                        loading={isLoading}
                                        disabled={isLoading || isDisabled}
                                        type={'link'}
                                    >
                                        {t('Unlink Dataset')}
                                    </Button>
                                </List.Item>
                            );
                        }}
                    ></List>
                );
            },
            width: '50%',
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, { id, name }) => {
                return (
                    <Flex vertical>
                    <Button
                        onClick={() => {
                            handleOpen(id);
                        }}
                        loading={isLoading}
                        disabled={isLoading || isDisabled}
                        type={'link'}
                    >
                        {t('Link Dataset')}
                    </Button>
                    <Popconfirm
                        title={t('Remove')}
                        description={t('Are you sure you want to delete the data output? This can have impact on downstream dependencies')}
                        onConfirm={() => onRemoveDataOutput(id, name)}
                        placement={'leftTop'}
                        okText={t('Confirm')}
                        cancelText={t('Cancel')}
                        okButtonProps={{ loading: isLoading }}
                        autoAdjustOverflow={true}
                    >
                    <Button
                        loading={isLoading}
                        disabled={isLoading || isDisabled}
                        type={'link'}
                    >
                        {t('Remove')}
                    </Button>
                    </Popconfirm>
                    </Flex>
                );
            },
        },
    ];
};
