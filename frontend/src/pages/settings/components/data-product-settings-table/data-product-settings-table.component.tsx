import type { TableProps } from 'antd';
import type { FormInstance } from 'antd';
import { Button, Flex, Form, Input, InputRef, Space, Table, Typography } from 'antd';
import type { ColumnGroupType, ColumnType } from 'antd/es/table/interface';
import { useContext, useEffect, useMemo, useRef, useState } from 'react';
import React from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal.tsx';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    useGetAllDataProductSettingsQuery,
    useRemoveDataProductSettingMutation,
    useUpdateDataProductSettingMutation,
} from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { DataProductSettingContract } from '@/types/data-product-setting';

import { CreateSettingModal } from '../new-data-product-setting-modal.component.tsx';
import styles from './data-product-settings-table.module.scss';
import { getDataProductTableColumns } from './data-product-settings-table-columns.tsx';

type Props = {
    scope: 'dataproduct' | 'dataset';
};

export function DataProductSettingsTable({ scope }: Props) {
    const { t } = useTranslation();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();

    const { data: dataProductSettings = [], isFetching } = useGetAllDataProductSettingsQuery();
    const filteredSettings = useMemo(() => {
        return dataProductSettings.filter((setting) => setting.scope === scope);
    }, [dataProductSettings, scope]);
    const [editDataProductSetting] = useUpdateDataProductSettingMutation();
    const [onRemoveDataProductSetting] = useRemoveDataProductSettingMutation();

    const columns = useMemo(
        () => getDataProductTableColumns({ t, handleOpen, onRemoveDataProductSetting }),
        [t, handleOpen, onRemoveDataProductSetting],
    );

    const onChange: TableProps<DataProductSettingContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const EditableContext = React.createContext<FormInstance<DataProductSettingContract> | null>(null);
    const EditableRow = ({ ...props }) => {
        const [form] = Form.useForm();
        return (
            <Form form={form} component={false}>
                <EditableContext.Provider value={form}>
                    <tr {...props} />
                </EditableContext.Provider>
            </Form>
        );
    };
    const handleAdd = () => {
        handleOpen();
    };
    const handleSave = async (row: DataProductSettingContract) => {
        try {
            await editDataProductSetting(row);
            dispatchMessage({ content: t('Data product setting updated successfully'), type: 'success' });
        } catch (_e) {
            dispatchMessage({ content: t('Could not update data product setting'), type: 'error' });
        }
    };
    interface EditableCellProps {
        title: React.ReactNode;
        editable: boolean;
        children: React.ReactNode;
        dataIndex: string;
        record: DataProductSettingContract;
        handleSave: (record: DataProductSettingContract) => void;
    }

    const EditableCell: React.FC<EditableCellProps> = ({
        title,
        editable,
        children,
        dataIndex,
        record,
        handleSave,
        ...restProps
    }) => {
        const [editing, setEditing] = useState(false);

        const inputRef = useRef<InputRef>(null);
        const form = useContext(EditableContext);

        useEffect(() => {
            if (editing) {
                inputRef.current?.focus();
            }
        }, [editing]);

        const toggleEdit = () => {
            setEditing(!editing);
            if (form) {
                form.setFieldsValue({
                    [dataIndex]: record[dataIndex as keyof DataProductSettingContract],
                });
            }
        };

        const save = async () => {
            try {
                if (form) {
                    const values = await form.validateFields();
                    toggleEdit();
                    handleSave({
                        ...record,
                        ...values,
                    });
                }
            } catch (errInfo) {
                console.error('Save failed:', errInfo);
            }
        };

        let childNode = children;
        if (editable) {
            childNode = editing ? (
                <Form.Item
                    style={{
                        margin: 0,
                    }}
                    name={dataIndex}
                    rules={[
                        {
                            required: dataIndex !== 'default',
                            message: `${title} is required.`,
                        },
                    ]}
                >
                    <Input ref={inputRef} onPressEnter={save} onBlur={save} />
                </Form.Item>
            ) : (
                <div
                    className="editable-cell-value-wrap"
                    style={{
                        paddingInlineEnd: 24,
                    }}
                    onClick={toggleEdit}
                >
                    {children}
                </div>
            );
        }
        return <td {...restProps}>{childNode}</td>;
    };

    const components = {
        body: {
            row: EditableRow,
            cell: EditableCell,
        },
    };

    const editableColumns = columns.map(
        (
            col:
                | (ColumnGroupType<DataProductSettingContract> & { editable?: boolean } & { dataIndex: number })
                | (ColumnType<DataProductSettingContract> & { editable?: boolean }),
        ) => {
            if (!col.editable) {
                return col;
            }
            return {
                ...col,
                onCell: (record: DataProductSettingContract) => ({
                    record,
                    editable: col.editable,
                    dataIndex: col.dataIndex,
                    title: col.title as string,
                    handleSave,
                }),
            };
        },
    );

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>
                    {scope === 'dataproduct' ? t('Data Product Settings') : t('Dataset Settings')}
                </Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {scope === 'dataproduct' ? t('Add Data Product Setting') : t('Add Dataset Setting')}
                    </Button>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<DataProductSettingContract>
                    components={components}
                    className={styles.table}
                    columns={editableColumns}
                    dataSource={filteredSettings}
                    onChange={onChange}
                    pagination={pagination}
                    rowKey={(record) => record.id}
                    loading={isFetching}
                    rowHoverable
                    rowClassName={() => 'editable-row'}
                    size={'small'}
                />
            </Flex>
            {isVisible && <CreateSettingModal scope={scope} onClose={handleClose} t={t} isOpen={isVisible} />}
        </Flex>
    );
}
