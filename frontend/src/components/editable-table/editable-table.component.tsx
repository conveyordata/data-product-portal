import { Form, Input, Table, InputRef } from 'antd';
import styles from './editable-table.module.scss';
import { useContext, useEffect, useRef, useState } from 'react';
import type { FormInstance } from 'antd';
import React from 'react';
import { ColumnType } from 'antd/es/table/interface';
import { TableProps } from 'antd/lib';

type Props<T> = Exclude<TableProps<T>, 'columns' | 'dataSource' | 'components'> & {
    data: T[];
    columns: EditableColumn<T>[];
    handleSave: (record: T) => void;
};

export type EditableColumn<T> = ColumnType<T> & { editable?: boolean };

export function EditableTable<TableData>({ data, columns, handleSave, ...tableProps }: Props<TableData>) {
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

    interface EditableCellProps {
        title: React.ReactNode;
        editable: boolean;
        children: React.ReactNode;
        dataIndex: string;
        record: TableData;
        handleSave: (record: TableData) => void;
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
                    [dataIndex]: record[dataIndex as keyof TableData],
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
                    style={{ margin: 0 }}
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
                <div className="editable-cell-value-wrap" onClick={toggleEdit}>
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

    const editableColumns = columns.map((col: EditableColumn<TableData>) => {
        if (!col.editable) {
            return col;
        }
        return {
            ...col,
            onCell: (record: TableData) => ({
                record,
                editable: col.editable,
                dataIndex: col.dataIndex,
                title: col.title as string,
                handleSave,
            }),
        };
    });

    return (
        <Table<TableData>
            components={components}
            className={styles.table}
            columns={editableColumns}
            dataSource={data}
            {...tableProps}
        />
    );
}
