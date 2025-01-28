import type { TableProps } from 'antd';
import { Button, Flex, Form, Input, Space, Table, Typography, InputRef } from 'antd';
import styles from './data-product-lifecycles-table.module.scss';
import { useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getDataProductTableColumns } from './data-product-lifecycles-table-columns.tsx';
import type { FormInstance } from 'antd';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import {
    useGetAllDataProductLifecyclesQuery,
    useRemoveDataProductLifecycleMutation,
    useUpdateDataProductLifecycleMutation,
} from '@/store/features/data-product-lifecycles/data-product-lifecycles-api-slice';
import { DataProductLifeCycleContract } from '@/types/data-product-lifecycle';
import React from 'react';
import { useModal } from '@/hooks/use-modal.tsx';
import { CreateLifecycleModal } from '../new-data-product-lifecycles-modal.component.tsx';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { ColumnGroupType, ColumnType } from 'antd/es/table/interface';

export function DataProductLifecyclesTable() {
    const { t } = useTranslation();
    const { data: dataProductLifecycles = [], isFetching } = useGetAllDataProductLifecyclesQuery();
    const [editDataProductLifecycle, { isLoading: isEditing }] = useUpdateDataProductLifecycleMutation();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();
    const [onRemoveDataProductLifecycle, { isLoading: isRemoving }] = useRemoveDataProductLifecycleMutation();

    const editColor = (record: DataProductLifeCycleContract, color: string) => {
        const new_record = { ...record, color: color };
        editDataProductLifecycle(new_record);
    };

    const columns = useMemo(
        () => getDataProductTableColumns({ t, handleOpen, editColor, onRemoveDataProductLifecycle }),
        [t, dataProductLifecycles],
    );

    const onChange: TableProps<DataProductLifeCycleContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const EditableContext = React.createContext<FormInstance<any> | null>(null);
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
    const handleSave = async (row: DataProductLifeCycleContract) => {
        try {
            await editDataProductLifecycle(row);
            dispatchMessage({ content: t('Data product lifecycle updated successfully'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Could not update data product lifecycle'), type: 'error' });
        }
    };
    interface EditableCellProps {
        title: React.ReactNode;
        editable: boolean;
        children: React.ReactNode;
        dataIndex: string;
        record: DataProductLifeCycleContract;
        handleSave: (record: DataProductLifeCycleContract) => void;
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
                    [dataIndex]: record[dataIndex as keyof DataProductLifeCycleContract],
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
                console.log('Save failed:', errInfo);
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
                            required: true,
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
                | (ColumnGroupType<DataProductLifeCycleContract> & { editable?: boolean } & { dataIndex: number })
                | (ColumnType<DataProductLifeCycleContract> & { editable?: boolean }),
        ) => {
            if (!col.editable) {
                return col;
            }
            return {
                ...col,
                onCell: (record: DataProductLifeCycleContract) => ({
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
                <Typography.Title level={3}>{t('Data Product Lifecycles')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Create Data Product Lifecycle')}
                    </Button>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <Table<DataProductLifeCycleContract>
                    components={components}
                    className={styles.table}
                    columns={editableColumns}
                    dataSource={dataProductLifecycles}
                    onChange={onChange}
                    pagination={pagination}
                    rowKey={(record) => record.id}
                    loading={isFetching}
                    rowHoverable
                    rowClassName={() => 'editable-row'}
                    size={'small'}
                />
            </Flex>
            {isVisible && <CreateLifecycleModal onClose={handleClose} t={t} isOpen={isVisible} />}
        </Flex>
    );
}
