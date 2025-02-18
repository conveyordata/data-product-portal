import type { TFunction } from 'i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import { EditableColumn } from '@/components/editable-table/editable-table.component';
import { DataProductIcon, DataProductTypesGetContract } from '@/types/data-product-type';
import { getDataProductTypeIcon } from '@/utils/data-product-type-icon.helper';
import { Button, Flex, Popconfirm, Select } from 'antd';
import Icon from '@ant-design/icons';
import styles from './data-product-type-table.module.scss';
import { dataProductIcons } from '@/types/data-product-type/data-product-type.contract';
const { Option } = Select;

type Props = {
    t: TFunction;
    handleRemove: (type: DataProductTypesGetContract) => void;
    handleEdit: (type: DataProductTypesGetContract) => () => void;
};

export const getDataProductTypeTableColumns = ({
    t,
    handleRemove,
    handleEdit,
}: Props): EditableColumn<DataProductTypesGetContract>[] => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
            editable: true,
        },
        {
            title: t('Description'),
            dataIndex: 'description',
            render: (description: string) => <TableCellItem text={description} tooltip={{ content: description }} />,
            editable: true,
        },
        {
            title: t('Icon'),
            dataIndex: 'icon_key',
            render: (icon_key: DataProductIcon) => {
                const icon = getDataProductTypeIcon(icon_key);
                return <TableCellItem reactSVGComponent={icon} />;
            },
            editable: true,
            formRender: (_, save) => {
                return (
                    <Select onSelect={save} onBlur={save}>
                        {dataProductIcons.map((icon) => (
                            <Option value={icon}>
                                <Icon component={getDataProductTypeIcon(icon)} className={styles.customIcon} />
                            </Option>
                        ))}
                    </Select>
                );
            },
        },
        {
            title: t('Actions'),
            key: 'action',
            width: '10%',
            render: (record) => {
                return (
                    <Flex>
                        <Button type={'link'} onClick={handleEdit(record)}>
                            {t('Edit')}
                        </Button>
                        <Popconfirm
                            title={t('Remove')}
                            description={t('Are you sure you want to delete the data product type?')}
                            onConfirm={() => handleRemove(record)}
                            placement={'leftTop'}
                            okText={t('Confirm')}
                            cancelText={t('Cancel')}
                            autoAdjustOverflow={true}
                        >
                            <Button type={'link'}>{t('Remove')}</Button>
                        </Popconfirm>
                    </Flex>
                );
            },
        },
    ];
};
