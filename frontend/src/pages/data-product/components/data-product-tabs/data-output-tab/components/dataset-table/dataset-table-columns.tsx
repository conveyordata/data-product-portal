import { Badge, Button, Flex, Popconfirm, type TableColumnsType, Tag } from 'antd';
import type { TFunction } from 'i18next';
import datasetbordericon from '@/assets/icons/dataset-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import type { DatasetContract } from '@/types/dataset';
import { getBadgeStatus, getStatusLabel } from '@/utils/status.helper';
import styles from './dataset-table.module.scss';

type Props = {
    t: TFunction;
    loading?: boolean;
    onRemoveDataset: (id: string, name: string) => void;
    getCanRemove: (datasetId: string) => boolean;
    onRemoveDataOutputLink?: (datasetId: string, dataOutputId: string) => void;
};

export const getDataProductDatasetsColumns = ({
    t,
    loading,
    onRemoveDataset,
    getCanRemove,
    onRemoveDataOutputLink,
}: Props): TableColumnsType<DatasetContract> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { id, name, status, description, data_output_links }) => {
                console.log('data_output_links', data_output_links);
                return (
                    <TableCellAvatar
                        popover={{ title: name, content: description }}
                        icon={<CustomSvgIconLoader iconComponent={datasetbordericon} />}
                        title={name}
                        subtitle={
                            <Flex vertical gap={4}>
                                <Badge
                                    status={getBadgeStatus(status)}
                                    text={getStatusLabel(t, status)}
                                    className={styles.noSelect}
                                />

                                {data_output_links && data_output_links.length > 0 && (
                                    <Flex wrap gap={4}>
                                        {data_output_links.map((link) => (
                                            <Tag
                                                key={link.data_output.id}
                                                color="blue"
                                                closable={!!onRemoveDataOutputLink}
                                                onClose={(e) => {
                                                    e.preventDefault();
                                                    onRemoveDataOutputLink?.(id, link.data_output.id);
                                                }}
                                            >
                                                {link.data_output.name}
                                            </Tag>
                                        ))}
                                    </Flex>
                                )}
                            </Flex>
                        }
                    />
                );
            },
            width: '30%',
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (_, { id, name }) => {
                const canRemove = getCanRemove(id);

                return (
                    <Flex vertical>
                        <Popconfirm
                            title={t('Remove')}
                            description={t(
                                'Are you sure you want to delete the dataset? This can have impact on downstream dependencies',
                            )}
                            onConfirm={() => onRemoveDataset(id, name)}
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            okButtonProps={{ loading: loading }}
                            autoAdjustOverflow={true}
                        >
                            <Button loading={loading} disabled={!canRemove} type={'link'}>
                                {t('Remove')}
                            </Button>
                        </Popconfirm>
                    </Flex>
                );
            },
        },
    ];
};
