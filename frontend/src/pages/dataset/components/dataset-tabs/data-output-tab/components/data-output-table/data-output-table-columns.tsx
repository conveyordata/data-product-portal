import { Badge, Button, Flex, Popconfirm, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import type { TechnicalAssetLink } from '@/store/api/services/generated/dataProductsOutputPortsApi.ts';
import type {
    ApproveOutputPortTechnicalAssetLinkApiArg,
    DenyOutputPortTechnicalAssetLinkApiArg,
} from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import type { UiElementMetadataResponse } from '@/store/api/services/generated/pluginsApi';
import { createDataOutputIdPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDataOutputIcon } from '@/utils/data-output-type.helper';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper';
import styles from './data-output-table.module.scss';

type Props = {
    t: TFunction;
    plugins?: UiElementMetadataResponse[];
    onRemoveDataOutputDatasetLink: (data_outputId: string, name: string) => void;
    onAcceptDataOutputDatasetLink: (request: ApproveOutputPortTechnicalAssetLinkApiArg) => void;
    onRejectDataOutputDatasetLink: (request: DenyOutputPortTechnicalAssetLinkApiArg) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
    canAccept?: boolean;
    canRevoke?: boolean;
};

export const getDatasetDataProductsColumns = ({
    t,
    plugins,
    onRemoveDataOutputDatasetLink,
    onAcceptDataOutputDatasetLink,
    onRejectDataOutputDatasetLink,
    isLoading,
    canAccept,
    canRevoke,
}: Props): TableColumnsType<TechnicalAssetLink> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Technical Asset name'),
            dataIndex: 'name',
            render: (_, { technical_asset, status }) => {
                return (
                    <TableCellAvatar
                        popover={{ title: technical_asset.name, content: technical_asset.description }}
                        linkTo={createDataOutputIdPath(technical_asset.id, technical_asset.owner_id)}
                        icon={
                            <CustomSvgIconLoader
                                iconComponent={getDataOutputIcon(
                                    technical_asset.configuration.configuration_type,
                                    plugins,
                                )}
                                size={'default'}
                            />
                        }
                        title={technical_asset.name}
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
            width: '100%',
        },
        {
            title: t('Actions'),
            key: 'action',
            hidden: !canAccept && !canRevoke,
            render: (_, { technical_asset, status, output_port_id, technical_asset_id }) => {
                if (status === DecisionStatus.Pending) {
                    return (
                        <Flex>
                            <Popconfirm
                                title={t('Allow Technical Asset Access')}
                                description={t('Are you sure you want to allow access to Technical Asset {{name}}?', {
                                    name: technical_asset.name,
                                })}
                                onConfirm={() =>
                                    onAcceptDataOutputDatasetLink({
                                        dataProductId: technical_asset.owner_id,
                                        outputPortId: output_port_id,
                                        approveLinkBetweenTechnicalAssetAndOutputPortRequest: {
                                            technical_asset_id: technical_asset_id,
                                        },
                                    })
                                }
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
                                title={t('Deny Technical Asset Access')}
                                description={t('Are you sure you want to deny access to Technical Asset {{name}}?', {
                                    name: technical_asset.name,
                                })}
                                onConfirm={() =>
                                    onRejectDataOutputDatasetLink({
                                        dataProductId: technical_asset.owner_id,
                                        outputPortId: output_port_id,
                                        denyLinkBetweenTechnicalAssetAndOutputPortRequest: {
                                            technical_asset_id: technical_asset_id,
                                        },
                                    })
                                }
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
                            title={t('Revoke Technical Asset Access')}
                            description={t('Are you sure you want to revoke access from Technical Asset {{name}}?', {
                                name: technical_asset.name,
                            })}
                            onConfirm={() =>
                                onRejectDataOutputDatasetLink({
                                    dataProductId: technical_asset.owner_id,
                                    outputPortId: output_port_id,
                                    denyLinkBetweenTechnicalAssetAndOutputPortRequest: {
                                        technical_asset_id: technical_asset_id,
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
                            onClick={() => onRemoveDataOutputDatasetLink(technical_asset_id, technical_asset.name)}
                        >
                            {t('Remove')}
                        </Button>
                    );
                }
            },
        },
    ];
};
