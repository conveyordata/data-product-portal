import { Badge, Button, Flex, Popconfirm, TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DataOutputSubtitle } from '@/components/data-outputs/data-output-subtitle/data-output-subtitle.component';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component';
import { DataOutputsGetContract } from '@/types/data-output/data-outputs-get.contract';
import { createDataOutputIdPath } from '@/types/navigation';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper';

import styles from './data-output-table.module.scss';

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
    isDisabled,
    isLoading,
    onRemoveDataOutput,
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
            render: (_, { id, owner_id, name, status, description, configuration }) => {
                return (
                    <TableCellAvatar
                        popover={{ title: name, content: description }}
                        linkTo={createDataOutputIdPath(id, owner_id)}
                        icon={
                            <CustomSvgIconLoader iconComponent={getDataOutputIcon(configuration.configuration_type)!} />
                        }
                        title={name}
                        subtitle={
                            <Flex vertical>
                                <Badge
                                    status={getBadgeStatus(status)}
                                    text={getStatusLabel(t, status)}
                                    className={styles.noSelect}
                                />
                            </Flex>
                        }
                    />
                );
            },
            width: '30%',
        },
        {
            title: t('Datasets'),
            render: (_, { dataset_links }) => {
                return (
                    <TableCellItem
                        icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                        text={t('linked to {{count}} datasets', { count: dataset_links.length })}
                    />
                );
            },
            width: '30%',
        },
        {
            title: t('Technical information'),
            render: (_, { id }) => {
                return <DataOutputSubtitle data_output_id={id} />;
            },
            width: '30%',
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (_, { id, name }) => {
                return (
                    <Flex vertical>
                        <Popconfirm
                            title={t('Remove')}
                            description={t(
                                'Are you sure you want to delete the data output? This can have impact on downstream dependencies',
                            )}
                            onConfirm={() => onRemoveDataOutput(id, name)}
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: isLoading }}
                            autoAdjustOverflow={true}
                        >
                            <Button loading={isLoading} disabled={isLoading || isDisabled} type={'link'}>
                                {t('Remove')}
                            </Button>
                        </Popconfirm>
                    </Flex>
                );
            },
        },
    ];
};
