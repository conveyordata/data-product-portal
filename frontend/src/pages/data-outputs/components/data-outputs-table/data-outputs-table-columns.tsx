import { Badge, TableColumnsType } from 'antd';
import { DataOutputsGetContract, DataOutputStatus } from '@/types/data-output';
import { TeamOutlined } from '@ant-design/icons';
import i18n from '@/i18n';
import { TFunction } from 'i18next';
import { TableStatusTag } from '@/components/list/table-status-tag/table-status-tag.component.tsx';
// import { DataOutputTypeContract } from '@/types/data-output-type';
// import { getDataOutputTypeIcon } from '@/utils/data-output-type-icon.helper.ts';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { BusinessAreaGetResponse } from '@/types/business-area';
import { getDataOutputIcon, getDataOutputType } from '@/utils/data-output-type.helper';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component';
import { createDataProductIdPath } from '@/types/navigation';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper';
import { getDataOutputDatasetLinkBadgeStatus, getDataOutputDatasetLinkStatusLabel } from '@/utils/status.helper';

const iconColumnWidth = 30;
export const getDataOutputTableColumns = ({ t }: { t: TFunction }): TableColumnsType<DataOutputsGetContract[0]> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: undefined,
            width: iconColumnWidth,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            filterSearch: true,
            defaultSortOrder: 'ascend',
            onFilter: (value, record) => record.name.startsWith(value as string),
            ellipsis: {
                showTitle: false,
            },
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
        },
        {
            title: t('Data Product'),
            dataIndex: 'owner',
            render: (_, { owner }) => {
                return (
                    <TableCellItem text={owner.name}/>
                );
            },
            width: '30%',
        },
        {
            title: t('Status'),
            dataIndex: 'status',
            render: (status: DataOutputStatus) => {
                return <TableStatusTag status={status} />;
            },
        },
        {
            title: t('Type'),
            dataIndex: 'configuration_type',
            filterSearch: true,
            onFilter: (value, record) => record.configuration_type.startsWith(value as string),
            render: (configuration_type: string) => {
                const icon = getDataOutputIcon(configuration_type);

                return <TableCellItem reactSVGComponent={icon} text={getDataOutputType(configuration_type, t)} />;
            },
            width: '30%',
        },
    ];
};
