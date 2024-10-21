import { PlatformServiceConfigContract } from '@/types/platform-service-config';
import { TFunction } from 'i18next';
import { TableColumnsType } from 'antd';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import deleteIcon from '@/assets/icons/delete-button.svg?react';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';

const iconColumnWidth = 100;
export const getPlatformConfigTableColumns = ({
    t,
}: {
    t: TFunction;
}): TableColumnsType<PlatformServiceConfigContract> => [
    {
        title: t('Id'),
        dataIndex: 'id',
        hidden: true,
    },
    {
        title: t('Platform Name'),
        dataIndex: 'platformName',
        filterSearch: true,
        defaultSortOrder: 'ascend',
        onFilter: (value, record) => record.platformName.startsWith(value as string),
        ellipsis: {
            showTitle: false,
        },
        render: (name: string) => {
            return <TableCellItem text={name} tooltip={{ content: name }} />;
        },
    },
    {
        title: t('Service Name'),
        dataIndex: 'serviceName',
        filterSearch: true,
        defaultSortOrder: 'ascend',
        onFilter: (value, record) => record.serviceName.startsWith(value as string),
        ellipsis: {
            showTitle: false,
        },
        render: (name: string) => {
            return <TableCellItem text={name} tooltip={{ content: name }} />;
        },
    },
    {
        title: undefined,
        width: iconColumnWidth,
        align: 'center',
        render: (_, record) => {
            const handleDelete = (id: string) => {
                console.log(`Deleting ${id}`);
                dispatchMessage({ content: t('Platform Service Configuration deleted successfully'), type: 'success' });
            };
            return (
                <div
                    onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(record.id);
                    }}
                >
                    <CustomSvgIconLoader iconComponent={deleteIcon} size="x-small" color={'dark'} />
                </div>
            );
        },
    },
];
