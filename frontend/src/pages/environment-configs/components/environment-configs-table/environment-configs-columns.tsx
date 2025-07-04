import { Flex, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import deleteIcon from '@/assets/icons/delete-button.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import type { EnvironmentConfigContract } from '@/types/environment';

const iconColumnWidth = 100;
export const getEnvironmentConfigTableColumns = ({
    t,
}: {
    t: TFunction;
}): TableColumnsType<EnvironmentConfigContract> => [
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
                dispatchMessage({ content: t('Environment configuration deleted successfully'), type: 'success' });
            };
            return (
                <Flex
                    onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(record.id);
                    }}
                >
                    <CustomSvgIconLoader iconComponent={deleteIcon} size="x-small" color={'dark'} />
                </Flex>
            );
        },
    },
];
