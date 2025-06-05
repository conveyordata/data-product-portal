import { Badge, Button, Flex, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import type { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset';
import type { DataOutputLink } from '@/types/dataset';
import { createDataOutputIdPath, createDataProductIdPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper';

import styles from './data-output-table.module.scss';

type Props = {
    t: TFunction;
    onRemoveDataOutputDatasetLink: (data_outputId: string, name: string, datasetLinkId: string) => void;
    onAcceptDataOutputDatasetLink: (request: DataOutputDatasetLinkRequest) => void;
    onRejectDataOutputDatasetLink: (request: DataOutputDatasetLinkRequest) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
    canAccept?: boolean;
    canRevoke?: boolean;
};

export const getDatasetDataProductsColumns = ({
    t,
    onRemoveDataOutputDatasetLink,
    onAcceptDataOutputDatasetLink,
    onRejectDataOutputDatasetLink,
    isLoading,
    canAccept,
    canRevoke,
}: Props): TableColumnsType<DataOutputLink> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Produced by Data Product'),
            dataIndex: 'dataproduct',
            render: (_, { data_output, status }) => {
                return (
                    <TableCellAvatar
                        linkTo={createDataProductIdPath(data_output.owner_id)}
                        icon={
                            <CustomSvgIconLoader
                                iconComponent={getDataProductTypeIcon(data_output.owner.type.icon_key)!}
                                hasRoundBorder
                                size={'default'}
                            />
                        }
                        title={data_output.owner.name}
                        subtitle={
                            <Badge
                                status={getDecisionStatusBadgeStatus(status)}
                                text={getDecisionStatusLabel(t, status)}
                                className={styles.noSelect}
                            />
                        }
                    />
                );
            },
            width: '50%',
        },
        {
            title: t('Data Output name'),
            dataIndex: 'name',
            render: (_, { data_output, status }) => {
                return (
                    <TableCellAvatar
                        popover={{ title: data_output.name, content: data_output.description }}
                        linkTo={createDataOutputIdPath(data_output.id, data_output.owner.id)}
                        icon={
                            <CustomSvgIconLoader
                                iconComponent={getDataOutputIcon(data_output.configuration.configuration_type)!}
                                size={'default'}
                            />
                        }
                        title={data_output.name}
                        subtitle={
                            <Badge
                                status={getDecisionStatusBadgeStatus(status)}
                                text={getDecisionStatusLabel(t, status)}
                                className={styles.noSelect}
                            />
                        }
                    />
                );
            },
            width: '50%',
        },
        {
            title: t('Actions'),
            key: 'action',
            hidden: !canAccept && !canRevoke,
            render: (_, { id, data_output, status, dataset_id, data_output_id }) => {
                if (status === DecisionStatus.Pending) {
                    return (
                        <Flex>
                            <Popconfirm
                                title={t('Allow Data Output Access')}
                                description={t('Are you sure you want to allow access to data output {{name}}?', {
                                    name: data_output.name,
                                })}
                                onConfirm={() => onAcceptDataOutputDatasetLink({ dataset_id, data_output_id, id })}
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button loading={isLoading} disabled={isLoading || !canAccept} type={'link'}>
                                    {t('Accept')}
                                </Button>
                            </Popconfirm>
                            <Popconfirm
                                title={t('Deny Data Output Access')}
                                description={t('Are you sure you want to deny access to data output {{name}}?', {
                                    name: data_output.name,
                                })}
                                onConfirm={() => onRejectDataOutputDatasetLink({ dataset_id, data_output_id, id })}
                                placement={'leftTop'}
                                okText={t('Confirm')}
                                cancelText={t('Cancel')}
                                okButtonProps={{ loading: isLoading }}
                                autoAdjustOverflow={true}
                            >
                                <Button loading={isLoading} disabled={isLoading || !canAccept} type={'link'}>
                                    {t('Reject')}
                                </Button>
                            </Popconfirm>
                        </Flex>
                    );
                }
                if (status === DecisionStatus.Approved) {
                    return (
                        <Popconfirm
                            title={t('Revoke Data Output Access')}
                            description={t('Are you sure you want to revoke access from data output {{name}}?', {
                                name: data_output.name,
                            })}
                            onConfirm={() => onRejectDataOutputDatasetLink({ dataset_id, data_output_id, id })}
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
                            onClick={() => onRemoveDataOutputDatasetLink(data_output_id, data_output.name, id)}
                        >
                            {t('Remove')}
                        </Button>
                    );
                }
            },
        },
    ];
};
