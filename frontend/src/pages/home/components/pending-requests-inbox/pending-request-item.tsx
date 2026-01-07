import { UserOutlined } from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import { Avatar, Button, Flex, List, Typography, theme } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';
import Justification from '@/components/data-products/data-product-dataset-justification/justification.component.tsx';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import { PosthogEvents } from '@/constants/posthog.constants';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import { type PendingAction, PendingActionTypes } from '@/types/pending-actions/pending-actions';
import { formatDate } from '@/utils/date.helper.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';
import styles from './pending-requests-inbox.module.scss';

type Props = {
    pendingAction: PendingAction;
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
            case PendingActionTypes.DataProductDataset:
                await handleAcceptDataProductDatasetLink({
                    id: pendingAction.id,
                    data_product_id: pendingAction.data_product_id,
                    dataset_id: pendingAction.dataset_id,
                });
                break;
            case PendingActionTypes.DataOutputDataset:
                await handleAcceptDataOutputDatasetLink({
                    id: pendingAction.id,
                    data_output_id: pendingAction.data_output_id,
                    dataset_id: pendingAction.dataset_id,
                });
                break;
            case PendingActionTypes.DataProductRoleAssignment:
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
            case PendingActionTypes.DataProductDataset:
                await handleRejectDataProductDatasetLink({
                    id: pendingAction.id,
                    data_product_id: pendingAction.data_product_id,
                    dataset_id: pendingAction.dataset_id,
                });
                break;
            case PendingActionTypes.DataOutputDataset:
                await handleRejectDataOutputDatasetLink({
                    id: pendingAction.id,
                    data_output_id: pendingAction.data_output_id,
                    dataset_id: pendingAction.dataset_id,
                });
                break;
            case PendingActionTypes.DataProductRoleAssignment:
                await handleDenyAccessToDataProduct({
                    assignment_id: pendingAction.id,
                    data_product_id: pendingAction.data_product.id,
                });
                break;
        }
    };

    const content = useMemo(() => {
        switch (pendingAction.pending_action_type) {
            case PendingActionTypes.DataProductDataset:
                return {
                    icon: <DatasetOutlined />,
                    color: datasetColor,
                    description: (
                        <Typography.Text>
                            {t('Request for read access from the data product ')}
                            <Link
                                onClick={(e) => e.stopPropagation()}
                                to={createDataProductIdPath(pendingAction.data_product_id)}
                            >
                                {pendingAction.data_product.name}
                            </Link>
                        </Typography.Text>
                    ),
                    message: (
                        <Flex vertical>
                            <Justification justification={pendingAction.justification} />
                            <Typography.Text>
                                {t('Accepting will grant the data product read access on the ')}
                                <Link
                                    onClick={(e) => e.stopPropagation()}
                                    to={createDatasetIdPath(pendingAction.dataset_id)}
                                >
                                    {pendingAction.dataset.name}
                                </Link>
                                {t(' output port.')}
                            </Typography.Text>
                        </Flex>
                    ),
                    tag: t('{{name}} Output port', { name: pendingAction.dataset.name }),
                    navigatePath: createDatasetIdPath(pendingAction.dataset_id, DatasetTabKeys.DataProduct),
                };

            case PendingActionTypes.DataOutputDataset:
                return {
                    icon: <DatasetOutlined />,
                    color: datasetColor,
                    description: (
                        <Typography.Text strong>
                            {t('Request for the creation of a link coming from the technical asset ')}
                            <Link
                                onClick={(e) => e.stopPropagation()}
                                to={createDataOutputIdPath(
                                    pendingAction.data_output_id,
                                    pendingAction.data_output.owner_id,
                                )}
                            >
                                {pendingAction.data_output.name}
                            </Link>
                        </Typography.Text>
                    ),
                    message: (
                        <Typography.Text>
                            {t('Accepting will create a link from the technical asset to the ')}
                            <Link
                                onClick={(e) => e.stopPropagation()}
                                to={createDatasetIdPath(pendingAction.dataset_id)}
                            >
                                {pendingAction.dataset.name}
                            </Link>
                            {t(' output port.')}
                        </Typography.Text>
                    ),
                    tag: t('{{name}} Output port', { name: pendingAction.dataset.name }),
                    navigatePath: createDatasetIdPath(pendingAction.dataset_id, DatasetTabKeys.DataOutput),
                };

            case PendingActionTypes.DataProductRoleAssignment:
                return {
                    icon: <DataProductOutlined />,
                    color: dataProductColor,
                    description: (
                        <Typography.Text strong>
                            {t('Request for team membership from ')}
                            {pendingAction.user.first_name} {pendingAction.user.last_name}
                        </Typography.Text>
                    ),
                    message: (
                        <Typography.Text>
                            {t('Accepting will grant the user the role of {{role}} in the ', {
                                role: pendingAction.role?.name,
                            })}
                            <Link
                                onClick={(e) => e.stopPropagation()}
                                to={createDataProductIdPath(pendingAction.data_product.id)}
                            >
                                {pendingAction.data_product.name}
                            </Link>
                            {t(' data product.')}
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
