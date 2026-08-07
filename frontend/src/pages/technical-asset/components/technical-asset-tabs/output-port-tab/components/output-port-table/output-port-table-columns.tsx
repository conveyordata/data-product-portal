import { Badge, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import outputPortBorderIcon from '@/assets/icons/border-icons/output-port-border-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
import { OutputPortPopoverTitle } from '@/components/output-ports/output-port-popover-title/output-port-popover-title.tsx';
import { OutputPortTitle } from '@/components/output-ports/output-port-title/output-port-title.tsx';
import { OutputPortActionButton } from '@/pages/technical-asset/components/technical-asset-tabs/output-port-tab/components/output-port-table/output-port-action-button.component.tsx';
import type { OutputPortLink } from '@/store/api/services/generated/dataProductsTechnicalAssetsApi.ts';
import { createMarketplaceOutputPortPath } from '@/types/navigation.ts';
import { DecisionStatus } from '@/types/roles';
import { getDecisionStatusBadgeStatus, getDecisionStatusLabel } from '@/utils/status.helper.ts';
import styles from './output-port-table.module.scss';

type Props = {
    t: TFunction;
    dataProductId: string;
};
export const getDataOutputDatasetsColumns = ({ t, dataProductId }: Props): TableColumnsType<OutputPortLink> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { output_port, status }) => {
                const isDatasetRequestApproved = status === DecisionStatus.Approved;
                const popoverTitle = (
                    <OutputPortPopoverTitle
                        name={output_port.name}
                        accessType={output_port.access_type}
                        isApproved={isDatasetRequestApproved}
                    />
                );
                return (
                    <TableCellAvatar
                        popover={{ title: popoverTitle, content: output_port.description }}
                        linkTo={createMarketplaceOutputPortPath(output_port.id, output_port.data_product_id)}
                        icon={<CustomSvgIconLoader iconComponent={outputPortBorderIcon} />}
                        title={<OutputPortTitle name={output_port.name} accessType={output_port.access_type} />}
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
            render: (_, { output_port, output_port_id, status }) => {
                return (
                    <OutputPortActionButton
                        outputPort={output_port}
                        technicalAssetId={output_port_id}
                        dataProductId={dataProductId}
                        status={status}
                    />
                );
            },
        },
    ];
};
