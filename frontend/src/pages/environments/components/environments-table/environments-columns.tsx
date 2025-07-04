import { Flex, type TableColumnsType } from 'antd';
import type { TFunction } from 'i18next';

import deleteIcon from '@/assets/icons/delete-button.svg?react';
import yesIcon from '@/assets/icons/yes-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import type { Environment } from '@/types/environment';

const iconColumnWidth = 100;
export const getEnvironmentTableColumns = ({ t }: { t: TFunction }): TableColumnsType<Environment> => [
    {
        title: t('Id'),
        dataIndex: 'id',
        hidden: true,
    },
    {
        title: t('Environment Name'),
        dataIndex: 'name',
        filterSearch: true,
        defaultSortOrder: 'ascend',
        onFilter: (value, record) => record.name.startsWith(value as string),
        ellipsis: {
            showTitle: false,
        },
        render: (name: string) => {
            return <TableCellItem text={name} tooltip={{ content: name }} />;
        },
    },
    {
        title: t('Default'),
        dataIndex: 'is_default',
        defaultSortOrder: 'ascend',
        ellipsis: {
            showTitle: false,
        },
        render: (isDefault: boolean) => {
            return <>{isDefault && <TableCellItem reactSVGComponent={yesIcon} />}</>;
        },
    },
    {
        title: undefined,
        width: iconColumnWidth,
        align: 'center',
        render: (_, record) => {
            const handleDelete = (id: string) => {
                console.log(`Deleting ${id}`);
                dispatchMessage({ content: t('Environment deleted successfully'), type: 'success' });
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
