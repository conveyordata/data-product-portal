import { UserOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Avatar, Button, Flex, List, Space, Tooltip, Typography, theme } from 'antd';
import { type ReactNode, useMemo } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';
import styled from 'styled-components';
import Justification from '@/components/data-products/data-product-dataset-justification/justification.component.tsx';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { PosthogEvents } from '@/constants/posthog.constants';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import {
    PendingRequestType_DataProductOutputPort,
    PendingRequestType_DataProductRoleAssignment,
    PendingRequestType_TechnicalAssetOutputPort,
} from '@/pages/home/components/pending-approvals-inbox/pending-approvals-types.tsx';
import type {
    DataProductOutputPortPendingAction,
    DataProductRoleAssignmentPendingAction,
    TechnicalAssetOutputPortPendingAction,
} from '@/store/api/services/generated/usersApi.ts';
import { createDataOutputIdPath, createDataProductIdPath, createMarketplaceOutputPortPath } from '@/types/navigation';
import { formatDate } from '@/utils/date.helper.ts';
import { usePendingActionHandlers } from '@/utils/pending-action.helper.ts';
import styles from './pending-approvals-inbox.module.scss';

type Props = {
    pendingAction:
        | DataProductOutputPortPendingAction
        | TechnicalAssetOutputPortPendingAction
        | DataProductRoleAssignmentPendingAction;
};

export function PendingItem({ pendingAction }: Props) {
    const posthog = usePostHog();
    const { t } = useTranslation();
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
        const first_name = pendingAction.requested_by?.first_name;
        const last_name = pendingAction.requested_by?.last_name;

        switch (pendingAction.pending_action_type) {
            case PendingRequestType_DataProductOutputPort: {
                const outputPortPath = createMarketplaceOutputPortPath(
                    pendingAction.output_port.id,
                    pendingAction.output_port.data_product_id,
                    DatasetTabKeys.Producers,
                );
                return {
                    icon: <DatasetOutlined />,
                    color: datasetColor,
                    description: (
                        <Trans t={t}>
                            {{ first_name }} {{ last_name }} requests read access to the{' '}
                            <Link onClick={(e) => e.stopPropagation()} to={outputPortPath}>
                                {pendingAction.output_port.name}
                            </Link>{' '}
                            Output Port
                            <br />
                            on behalf of the{' '}
                            <Link
                                onClick={(e) => e.stopPropagation()}
                                to={createDataProductIdPath(pendingAction.data_product_id)}
                            >
                                {pendingAction.data_product.name}
                            </Link>{' '}
                            Data Product
                        </Trans>
                    ),
                    justification: <Justification justification={pendingAction.justification} />,
                    tooltip: t(
                        'Accepting will grant the {{ data_product }} Data Product read access to the {{ output_port }} Output Port',
                        {
                            data_product: pendingAction.data_product.name,
                            output_port: pendingAction.output_port.name,
                        },
                    ),
                    tag: t('{{name}} Output Port', { name: pendingAction.output_port.name }),
                    navigatePath: outputPortPath,
                };
            }

            case PendingRequestType_TechnicalAssetOutputPort: {
                const marketplacePath = createMarketplaceOutputPortPath(
                    pendingAction.output_port.id,
                    pendingAction.output_port.data_product_id,
                    DatasetTabKeys.Consumers,
                );
                return {
                    icon: <DatasetOutlined />,
                    color: datasetColor,
                    description: (
                        <Trans t={t}>
                            {{ first_name }} {{ last_name }} requests the addition of the Technical Asset{' '}
                            <Link
                                onClick={(e) => e.stopPropagation()}
                                to={createDataOutputIdPath(
                                    pendingAction.technical_asset_id,
                                    pendingAction.technical_asset.owner_id,
                                )}
                            >
                                {pendingAction.technical_asset.name}
                            </Link>
                            <br />
                            to the{' '}
                            <Link onClick={(e) => e.stopPropagation()} to={marketplacePath}>
                                {pendingAction.output_port.name}
                            </Link>{' '}
                            Output Port
                        </Trans>
                    ),
                    tooltip: t('Accepting will expose the Technical Asset through the {{ output_port }} Output Port.', {
                        output_port: pendingAction.output_port.name,
                    }),
                    tag: t('{{name}} Output Port', { name: pendingAction.output_port.name }),
                    navigatePath: marketplacePath,
                };
            }

            case PendingRequestType_DataProductRoleAssignment: {
                const role = pendingAction.role?.name;
                return {
                    icon: <DataProductOutlined />,
                    color: dataProductColor,
                    description: (
                        <Trans t={t}>
                            {{ first_name }} {{ last_name }} requests to become {{ role }} for the{' '}
                            <Link
                                onClick={(e) => e.stopPropagation()}
                                to={createDataProductIdPath(pendingAction.data_product.id)}
                            >
                                {pendingAction.data_product.name}
                            </Link>{' '}
                            Data Product
                        </Trans>
                    ),
                    tooltip: t(
                        'Accepting will grant the user the role of {{ role }} in the {{ data_product }} Data Product',
                        {
                            data_product: pendingAction.data_product.name,
                        },
                    ),
                    tag: t('{{name}} Data Product', { name: pendingAction.data_product.name }),
                    navigatePath: createDataProductIdPath(pendingAction.data_product.id, DataProductTabKeys.Team),
                };
            }
        }
    }, [pendingAction, dataProductColor, datasetColor, t]);

    if (!content) return null;

    const getInitials = (firstName: string, lastName: string) =>
        (firstName?.charAt(0) || '') + (lastName?.charAt(0) || '');

    const formattedDate = pendingAction.requested_on ? formatDate(pendingAction.requested_on) : '';

    const actions = (tooltip: ReactNode) => [
        <Tooltip
            key="accept"
            title={tooltip}
            placement="bottomLeft"
            styles={{ root: { width: 'fit-content', maxWidth: '80%' } }}
            arrow={{ pointAtCenter: true }}
        >
            <Button
                onClick={async (e) => {
                    e.stopPropagation();
                    await handleAccept();
                }}
                type="link"
                size="small"
            >
                {t('Accept')}
            </Button>
        </Tooltip>,
        <Button
            key="reject"
            onClick={async (e) => {
                e.stopPropagation();
                await handleDeny();
            }}
            type="link"
            size="small"
        >
            {t('Reject')}
        </Button>,
    ];

    const StyledMeta = styled(List.Item.Meta)`
  /* Target the internal title class */
  .ant-list-item-meta-title {
    margin-bottom: 0 !important;
  }
`;

    return (
        <List.Item
            className={styles.listItem}
            onClick={() => navigate(content.navigatePath)}
            actions={actions(content.tooltip)}
            styles={{
                actions: {
                    marginTop: 0,
                    marginInlineStart: 'var(--ant-margin-xxl)',
                },
            }}
            extra={
                <Space vertical align="end">
                    <Flex gap="small">
                        <Typography.Text type="secondary">{content.icon}</Typography.Text>
                        <Typography.Text style={{ color: content.color }} strong>
                            {content.tag}
                        </Typography.Text>
                    </Flex>
                    {formattedDate}
                </Space>
            }
        >
            <StyledMeta
                avatar={
                    <Avatar style={{ backgroundColor: content.color }}>
                        {getInitials(
                            pendingAction.requested_by?.first_name ?? '',
                            pendingAction.requested_by?.last_name ?? '',
                        ) || <UserOutlined />}
                    </Avatar>
                }
                title={<Typography.Text style={{ marginBottom: 0 }}>{content.description}</Typography.Text>}
                description={content.justification}
                style={{ marginBottom: '8px' }}
            />
        </List.Item>
    );
}
