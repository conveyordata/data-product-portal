import { UserOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Avatar, Button, Flex, List, Typography, theme } from 'antd';
import { useMemo } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';
import Justification from '@/components/data-products/data-product-dataset-justification/justification.component.tsx';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { PosthogEvents } from '@/constants/posthog.constants';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import type {
    DataProductOutputPortPendingAction,
    DataProductRoleAssignmentPendingAction,
    TechnicalAssetOutputPortPendingAction,
} from '@/store/api/services/generated/usersApi.ts';
import { createDataOutputIdPath, createDataProductIdPath, createMarketplaceOutputPortPath } from '@/types/navigation';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/types/pending-actions/pending-request-types';
import { formatDate } from '@/utils/date.helper.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';
import styles from './pending-requests-inbox.module.scss';

type Props = {
    pendingAction:
        | DataProductOutputPortPendingAction
        | TechnicalAssetOutputPortPendingAction
        | DataProductRoleAssignmentPendingAction;
};

export function PendingItem({ pendingAction }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const {
        token: { colorPrimary: dataProductColor, colorPrimaryActive: datasetColor },
    } = theme.useToken();

    const navigate = useNavigate();
    const {
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,
        handleAcceptDataOutputDatasetLink,
        handleRejectDataOutputDatasetLink,
        handleGrantAccessToDataProduct,
        handleDenyAccessToDataProduct,
    } = usePendingActionHandlers();

    const handleAccept = async () => {
        posthog.capture(PosthogEvents.REQUESTS_ACCEPT);
        switch (pendingAction.pending_action_type) {
            case PendingRequestType_DataProductOutputPort:
                await handleAcceptDataProductDatasetLink({
                    dataProductId: pendingAction.output_port.data_product_id,
                    outputPortId: pendingAction.output_port.id,
                    approveOutputPortAsInputPortRequest: {
                        consuming_data_product_id: pendingAction.data_product.id,
                    },
                });
                break;
            case PendingRequestType_TechnicalAssetOutputPort:
                await handleAcceptDataOutputDatasetLink({
                    dataProductId: pendingAction.output_port.data_product_id,
                    outputPortId: pendingAction.output_port_id,
                    approveLinkBetweenTechnicalAssetAndOutputPortRequest: {
                        technical_asset_id: pendingAction.technical_asset_id,
                    },
                });
                break;
            case PendingRequestType_DataProductRoleAssignment:
                await handleGrantAccessToDataProduct({
                    assignment_id: pendingAction.id,
                    data_product_id: pendingAction.data_product.id,
                });
                break;
        }
    };

    const handleDeny = async () => {
        posthog.capture(PosthogEvents.REQUESTS_REJECT);
        switch (pendingAction.pending_action_type) {
            case PendingRequestType_DataProductOutputPort:
                await handleRejectDataProductDatasetLink({
                    dataProductId: pendingAction.output_port.data_product_id,
                    outputPortId: pendingAction.output_port.id,
                    denyOutputPortAsInputPortRequest: {
                        consuming_data_product_id: pendingAction.data_product.id,
                    },
                });
                break;
            case PendingRequestType_TechnicalAssetOutputPort:
                await handleRejectDataOutputDatasetLink({
                    dataProductId: pendingAction.output_port.data_product_id,
                    outputPortId: pendingAction.output_port_id,
                    denyLinkBetweenTechnicalAssetAndOutputPortRequest: {
                        technical_asset_id: pendingAction.technical_asset_id,
                    },
                });
                break;
            case PendingRequestType_DataProductRoleAssignment:
                await handleDenyAccessToDataProduct({
                    assignment_id: pendingAction.id,
                    data_product_id: pendingAction.data_product.id,
                });
                break;
        }
    };

    const content = useMemo(() => {
        switch (pendingAction.pending_action_type) {
            case PendingRequestType_DataProductOutputPort:
                return {
                    icon: <DatasetOutlined />,
                    color: datasetColor,
                    description: (
                        <Typography.Text>
                            <Trans t={t}>
                                Request for read access from the Data Product{' '}
                                <Link
                                    onClick={(e) => e.stopPropagation()}
                                    to={createDataProductIdPath(pendingAction.data_product_id)}
                                >
                                    {pendingAction.data_product.name}
                                </Link>
                            </Trans>
                        </Typography.Text>
                    ),
                    message: (
                        <Flex vertical>
                            <Justification justification={pendingAction.justification} />
                            <Typography.Text>
                                <Trans t={t}>
                                    Accepting will grant the Data Product read access on the{' '}
                                    <Link
                                        onClick={(e) => e.stopPropagation()}
                                        to={createMarketplaceOutputPortPath(
                                            pendingAction.output_port_id,
                                            pendingAction.output_port.data_product_id,
                                        )}
                                    >
                                        {pendingAction.output_port.name}
                                    </Link>{' '}
                                    Output Port.
                                </Trans>
                            </Typography.Text>
                        </Flex>
                    ),
                    tag: t('{{name}} Output Port', { name: pendingAction.output_port.name }),
                    navigatePath: createMarketplaceOutputPortPath(
                        pendingAction.output_port.id,
                        pendingAction.output_port.data_product_id,
                        DatasetTabKeys.Producers,
                    ),
                };

            case PendingRequestType_TechnicalAssetOutputPort:
                return {
                    icon: <DatasetOutlined />,
                    color: datasetColor,
                    description: (
                        <Typography.Text strong>
                            <Trans t={t}>
                                Request for the creation of a link coming from the Technical Asset{' '}
                                <Link
                                    onClick={(e) => e.stopPropagation()}
                                    to={createDataOutputIdPath(
                                        pendingAction.technical_asset_id,
                                        pendingAction.technical_asset.owner_id,
                                    )}
                                >
                                    {pendingAction.technical_asset.name}
                                </Link>
                            </Trans>
                        </Typography.Text>
                    ),
                    message: (
                        <Typography.Text>
                            <Trans t={t}>
                                Accepting will create a link from the Technical Asset to the{' '}
                                <Link
                                    onClick={(e) => e.stopPropagation()}
                                    to={createMarketplaceOutputPortPath(
                                        pendingAction.output_port_id,
                                        pendingAction.output_port.data_product_id,
                                    )}
                                >
                                    {pendingAction.output_port.name}
                                </Link>{' '}
                                Output Port.
                            </Trans>
                        </Typography.Text>
                    ),
                    tag: t('{{name}} Output Port', { name: pendingAction.output_port.name }),
                    navigatePath: createMarketplaceOutputPortPath(
                        pendingAction.output_port.id,
                        pendingAction.output_port.data_product_id,
                        DatasetTabKeys.Consumers,
                    ),
                };

            case PendingRequestType_DataProductRoleAssignment:
                return {
                    icon: <DataProductOutlined />,
                    color: dataProductColor,
                    description: (
                        <Typography.Text strong>
                            {t('Request for team membership from {{first_name}} {{last_name}}', {
                                first_name: pendingAction.user.first_name,
                                last_name: pendingAction.user.last_name,
                            })}
                        </Typography.Text>
                    ),
                    message: (
                        <Typography.Text>
                            <Trans t={t}>
                                Accepting will grant the user the role of {pendingAction.role?.name} in the{' '}
                                <Link
                                    onClick={(e) => e.stopPropagation()}
                                    to={createDataProductIdPath(pendingAction.data_product.id)}
                                >
                                    {pendingAction.data_product.name}
                                </Link>{' '}
                                Data Product.
                            </Trans>
                        </Typography.Text>
                    ),
                    tag: t('{{name}} Data Product', { name: pendingAction.data_product.name }),
                    navigatePath: createDataProductIdPath(pendingAction.data_product.id, DataProductTabKeys.Team),
                };
        }
    }, [pendingAction, dataProductColor, datasetColor, t]);

    if (!content) return null;

    const getInitials = (firstName: string, lastName: string) =>
        (firstName?.charAt(0) || '') + (lastName?.charAt(0) || '');

    const formattedDate = pendingAction.requested_on ? formatDate(pendingAction.requested_on) : '';

    return (
        <List.Item
            className={styles.listItem}
            onClick={() => navigate(content.navigatePath)}
            actions={[
                <Button
                    key="accept"
                    onClick={(e) => {
                        e.stopPropagation();
                        handleAccept();
                    }}
                    type="link"
                    size="small"
                >
                    {t('Accept')}
                </Button>,
                <Button
                    key="reject"
                    onClick={(e) => {
                        e.stopPropagation();
                        handleDeny();
                    }}
                    type="link"
                    size="small"
                >
                    {t('Reject')}
                </Button>,
            ]}
            extra={
                <Flex gap="small">
                    <Typography.Text type="secondary">{content.icon}</Typography.Text>
                    <Typography.Text style={{ color: content.color }} strong>
                        {content.tag}
                    </Typography.Text>
                </Flex>
            }
        >
            <List.Item.Meta
                avatar={
                    <Avatar style={{ backgroundColor: content.color }}>
                        {getInitials(
                            pendingAction.requested_by?.first_name ?? '',
                            pendingAction.requested_by?.last_name ?? '',
                        ) || <UserOutlined />}
                    </Avatar>
                }
                title={content.description}
                description={`${t('by')} ${pendingAction.requested_by?.first_name ?? ''} ${pendingAction.requested_by?.last_name ?? ''}, ${formattedDate}`}
            />
            {content.message}
        </List.Item>
    );
}
