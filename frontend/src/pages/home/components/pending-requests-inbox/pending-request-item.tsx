import { UserOutlined } from '@ant-design/icons';
import { Avatar, Button, Flex, List, Typography, theme } from 'antd';
import type { TFunction } from 'i18next';
import type { ReactElement, ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, useNavigate } from 'react-router';
import Justification from '@/components/data-products/data-product-dataset-justification/justification.component.tsx';
import { DataProductOutlined, DatasetOutlined } from '@/components/icons';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import type { DataOutputDatasetLinkRequest } from '@/types/data-output-dataset';
import type { DataProductDatasetLinkRequest } from '@/types/data-product-dataset';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation';
import {
    type ActionResolveRequest,
    type PendingAction,
    PendingActionTypes,
} from '@/types/pending-actions/pending-actions';
import type { DataProductRoleRequest } from '@/types/roles';
import type { UserContract } from '@/types/users';
import { formatDate } from '@/utils/date.helper.ts';
import { usePendingActionHandlers } from '@/utils/pending-request.helper';
import styles from './pending-requests-inbox.module.scss';

export type PendingActionItem = {
    key: string;
    description: ReactNode;
    navigatePath: string;
    date: string;
    author: string;
    initials: string;
    message: ReactNode;
    color: string;
    tag: ReactNode;
    type: PendingActionTypes;
    request: ActionResolveRequest;
    icon: ReactNode;
};

export const createPendingItem = (action: PendingAction, t: TFunction, color: string): PendingActionItem => {
    let link: string;
    let description: ReactElement;
    let navigatePath: string;
    let actor: UserContract;
    let message: ReactElement;
    let tag: ReactElement;
    let type: PendingActionTypes;
    let request: ActionResolveRequest;
    let icon: ReactElement;

    function getInitials(firstName: string, lastName: string) {
        return (firstName?.charAt(0) || '') + (lastName ? lastName.charAt(0) : '');
    }
    switch (action.pending_action_type) {
        case PendingActionTypes.DataProductDataset:
            icon = <DatasetOutlined />;
            link = createDataProductIdPath(action.data_product_id);
            description = (
                <Typography.Text>
                    {t('Request for read access from the data product ')}
                    <Link onClick={(e) => e.stopPropagation()} to={link}>
                        {action.data_product.name}
                    </Link>
                </Typography.Text>
            );
            message = (
                <Flex vertical>
                    <Justification justification={action.justification} />
                    <Typography.Text>
                        {t('Accepting will grant the data product read access on the ')}
                        <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                            {action.dataset.name}
                        </Link>
                        {t(' output port.')}
                    </Typography.Text>
                </Flex>
            );
            tag = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('{{name}} Output port', { name: action.dataset.name })}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataProduct);
            actor = action.requested_by;
            type = PendingActionTypes.DataProductDataset as PendingActionTypes.DataProductDataset;
            request = {
                type: PendingActionTypes.DataProductDataset as PendingActionTypes.DataProductDataset,
                request: {
                    id: action.id,
                    data_product_id: action.data_product_id,
                    dataset_id: action.dataset_id,
                },
            };
            break;

        case PendingActionTypes.DataOutputDataset:
            icon = <DatasetOutlined color="" />;
            link = createDataOutputIdPath(action.data_output_id, action.data_output.owner_id);
            description = (
                <Typography.Text strong>
                    {t('Request for the creation of a link coming from the technical asset ')}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        {action.data_output.name}
                    </Link>
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Accepting will create a link from the technical asset to the ')}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.dataset_id)}>
                        {action.dataset.name}
                    </Link>
                    {t(' output port.')}
                </Typography.Text>
            );
            tag = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('{{name}} Output port', { name: action.dataset.name })}
                </Typography.Text>
            );
            navigatePath = createDatasetIdPath(action.dataset_id, DatasetTabKeys.DataOutput);
            actor = action.requested_by;
            type = PendingActionTypes.DataOutputDataset as PendingActionTypes.DataOutputDataset;
            request = {
                type: PendingActionTypes.DataOutputDataset as PendingActionTypes.DataOutputDataset,
                request: {
                    id: action.id,
                    data_output_id: action.data_output_id,
                    dataset_id: action.dataset_id,
                },
            };
            break;

        case PendingActionTypes.DataProductRoleAssignment:
            icon = <DataProductOutlined />;
            link = createDataProductIdPath(action.data_product.id);
            description = (
                <Typography.Text strong>
                    {t('Request for team membership from ')}
                    <Link onClick={(e) => e.stopPropagation()} to={'/'}>
                        {action.user.first_name} {action.user.last_name}
                    </Link>
                </Typography.Text>
            );
            message = (
                <Typography.Text>
                    {t('Accepting will grant the user the role of {{role}} in the', {
                        role: action.role.name,
                        firstName: action.user.first_name,
                        lastName: action.user.last_name,
                    })}
                    <Link onClick={(e) => e.stopPropagation()} to={createDatasetIdPath(action.data_product.id)}>
                        {action.data_product.name}
                    </Link>
                    {t(' data product.')}
                </Typography.Text>
            );
            tag = (
                <Typography.Text
                    style={{
                        color: color,
                    }}
                    strong
                >
                    {t('{{name}} Data Product', { name: action.data_product.name })}
                </Typography.Text>
            );
            navigatePath = createDataProductIdPath(action.data_product.id, DataProductTabKeys.Team);
            actor = action.user;
            type = PendingActionTypes.DataProductRoleAssignment as PendingActionTypes.DataProductRoleAssignment;
            request = {
                type: PendingActionTypes.DataProductRoleAssignment as PendingActionTypes.DataProductRoleAssignment,
                request: { assignment_id: action.id, data_product_id: action.data_product.id },
            };
            break;

        default:
            throw new Error('Unknown pending action type');
    }

    return {
        key: type + action.id,
        description: description,
        navigatePath: navigatePath,
        date: action.requested_on ?? '',
        author: `${actor.first_name} ${actor.last_name}`,
        initials: getInitials(actor.first_name, actor.last_name),
        message: message,
        color: color,
        tag: tag,
        type: action.pending_action_type,
        request: request,
        icon: icon,
    };
};

export type Props = {
    pendingAction: PendingAction;
};

export function PendingItem({ pendingAction }: Props) {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const {
        token: { colorPrimary: dataProductColor, colorPrimaryActive: datasetColor },
    } = theme.useToken();
    const item = createPendingItem(
        pendingAction,
        t,
        pendingAction.pending_action_type === PendingActionTypes.DataOutputDataset ||
            pendingAction.pending_action_type === PendingActionTypes.DataProductDataset
            ? datasetColor
            : dataProductColor,
    );
    const {
        handleAcceptDataProductDatasetLink,
        handleRejectDataProductDatasetLink,
        handleAcceptDataOutputDatasetLink,
        handleRejectDataOutputDatasetLink,
        handleGrantAccessToDataProduct,
        handleDenyAccessToDataProduct,
    } = usePendingActionHandlers();

    const handleAccept = () => {
        const request = item.request.request;
        switch (item.type) {
            case PendingActionTypes.DataProductDataset:
                handleAcceptDataProductDatasetLink(request as DataProductDatasetLinkRequest);
                break;
            case PendingActionTypes.DataOutputDataset:
                handleAcceptDataOutputDatasetLink(request as DataOutputDatasetLinkRequest);
                break;
            case PendingActionTypes.DataProductRoleAssignment:
                handleGrantAccessToDataProduct(request as DataProductRoleRequest);
                break;
        }
    };

    const handleDeny = () => {
        const request = item.request.request;
        switch (item.type) {
            case PendingActionTypes.DataProductDataset:
                handleRejectDataProductDatasetLink(request as DataProductDatasetLinkRequest);
                break;
            case PendingActionTypes.DataOutputDataset:
                handleRejectDataOutputDatasetLink(request as DataOutputDatasetLinkRequest);
                break;
            case PendingActionTypes.DataProductRoleAssignment:
                handleDenyAccessToDataProduct(request as DataProductRoleRequest);
                break;
        }
    };

    const formattedDate = item.date ? formatDate(item.date) : '';
    return (
        <List.Item
            className={styles.listItem}
            key={item.key}
            onClick={() => navigate(item.navigatePath)}
            actions={[
                <Button
                    key={'accept'}
                    onClick={(e) => {
                        e.stopPropagation();
                        posthog.capture(PosthogEvents.REQUESTS_ACCEPT);
                        handleAccept();
                    }}
                    type="link"
                    size={'small'}
                >
                    {t('Accept')}
                </Button>,
                <Button
                    key={'reject'}
                    onClick={(e) => {
                        e.stopPropagation();
                        posthog.capture(PosthogEvents.REQUESTS_REJECT);
                        handleDeny();
                    }}
                    type="link"
                    size={'small'}
                >
                    {t('Reject')}
                </Button>,
            ]}
            extra={
                <Flex gap="small">
                    <Typography.Text type="secondary">{item.icon}</Typography.Text>
                    <Typography.Text>{item.tag}</Typography.Text>
                </Flex>
            }
        >
            <List.Item.Meta
                avatar={<Avatar style={{ backgroundColor: item.color }}>{item.initials || <UserOutlined />}</Avatar>}
                title={item.description}
                description={
                    <>
                        {t('by')} {item.author}, {formattedDate}
                    </>
                }
            />
            {item.message}
        </List.Item>
    );
}
