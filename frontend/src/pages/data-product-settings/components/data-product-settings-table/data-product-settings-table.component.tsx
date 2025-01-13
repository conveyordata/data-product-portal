import type { RadioChangeEvent, TableProps } from 'antd';
import { Button, Flex, Form, Input, Space, Table, Typography } from 'antd';
import styles from './data-product-settings-table.module.scss';
import { Link, useNavigate } from 'react-router-dom';
import { ApplicationPaths, createDataProductIdPath } from '@/types/navigation.ts';
import {
    useGetAllDataProductsQuery,
    useGetUserDataProductsQuery,
} from '@/store/features/data-products/data-products-api-slice.ts';
import { useContext, useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { getDataProductTableColumns } from './data-product-settings-table-columns.tsx';
import { DataProductsGetContract } from '@/types/data-product';
import { SearchForm } from '@/types/shared';
import { useSelector } from 'react-redux';
import { selectCurrentUser } from '@/store/features/auth/auth-slice.ts';
import { TableQuickFilter } from '@/components/list/table-quick-filter/table-quick-filter.tsx';
import { useQuickFilter } from '@/hooks/use-quick-filter.tsx';
import { QuickFilterParticipation } from '@/types/shared/table-filters.ts';
import { useTablePagination } from '@/hooks/use-table-pagination.tsx';
import { useCreateDataProductSettingMutation, useCreateDataProductSettingValueMutation, useGetAllDataProductSettingsQuery, useRemoveDataProductSettingMutation, useUpdateDataProductSettingMutation } from '@/store/features/data-product-settings/data-product-settings-api-slice';
import { DataProductSettingContract } from '@/types/data-product-setting';
import React from 'react';
import { useModal } from '@/hooks/use-modal.tsx';
import { CreateSettingModal } from '../new-data-product-setting-modal.component.tsx';

export function DataProductSettingsTable() {
    const currentUser = useSelector(selectCurrentUser);
    const { t } = useTranslation();
    const { quickFilter, onQuickFilterChange, quickFilterOptions } = useQuickFilter({});
    const navigate = useNavigate();
    const { data: dataProductSettings = [], isFetching } = useGetAllDataProductSettingsQuery();
    const [editDataProductSetting, { isLoading: isEditing }] = useUpdateDataProductSettingMutation();
    const [createDataProductSetting, {isLoading: isCreating}] = useCreateDataProductSettingMutation();
    const { data: userDataProducts = [], isFetching: isFetchingUserDataProducts } = useGetUserDataProductsQuery(
        currentUser?.id || '',
        { skip: !currentUser },
    );
    const { pagination, handlePaginationChange, handleTotalChange, resetPagination } = useTablePagination({});
    const [searchForm] = Form.useForm<SearchForm>();
    const { isVisible, handleOpen, handleClose } = useModal();
    const [onRemoveDataProductSetting, {isLoading: isRemoving}] = useRemoveDataProductSettingMutation();
    const searchTerm = Form.useWatch('search', searchForm);

    const columns = useMemo(() => getDataProductTableColumns({ t, handleOpen, onRemoveDataProductSetting}), [t, dataProductSettings]);

    const onChange: TableProps<DataProductSettingContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    function navigateToDataProduct(dataProductId: string) {
        navigate(createDataProductIdPath(dataProductId));
    }

    const handleQuickFilterChange = ({ target: { value } }: RadioChangeEvent) => {
        onQuickFilterChange(value);
        resetPagination();
    };

    useEffect(() => {
        if (!isFetching && !isFetchingUserDataProducts) {
            if (quickFilter === QuickFilterParticipation.All) {
                handleTotalChange(dataProductSettings.length);
            } else {
                handleTotalChange(userDataProducts.length);
            }
        }
    }, [quickFilter, isFetching, isFetchingUserDataProducts]);
    const EditableContext = React.createContext(null);
    const EditableRow = ({ index, ...props }) => {
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
        // TODO Modal
        handleOpen()
    };
      const handleSave = (row) => {
        console.log(row);
        editDataProductSetting(row)
        // const newData = [...dataSource];
        // const index = newData.findIndex((item) => row.key === item.key);
        // const item = newData[index];
        // newData.splice(index, 1, {
        //   ...item,
        //   ...row,
        // });
        // setDataSource(newData);
      };
    const EditableCell = ({
        title,
        editable,
        children,
        dataIndex,
        record,
        handleSave,
        ...restProps
      }) => {
        const [editing, setEditing] = useState(false);
        const inputRef = useRef(null);
        const form = useContext(EditableContext);
        useEffect(() => {
          if (editing) {
            inputRef.current?.focus();
          }
        }, [editing]);
        const toggleEdit = () => {
          setEditing(!editing);
          form.setFieldsValue({
            [dataIndex]: record[dataIndex],
          });
        };
        const save = async () => {
          try {
            const values = await form.validateFields();
            toggleEdit();
            handleSave({
              ...record,
              ...values,
            });
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
      const editableColumns = columns.map((col) => {
        if (!col.editable) {
          return col;
        }
        return {
          ...col,
          onCell: (record) => ({
            record,
            editable: col.editable,
            dataIndex: col.dataIndex,
            title: col.title,
            handleSave,
          }),
        };
      });
    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Data Product Settings')}</Typography.Title>
                {/* <Form<SearchForm> form={searchForm} className={styles.searchForm}>
                    <Form.Item<SearchForm> name={'search'} initialValue={''} className={styles.formItem}>
                        <Input.Search placeholder={t('Search data products by name')} allowClear />
                    </Form.Item>
                </Form> */}
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Create Data Product Setting')}
                    </Button>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                {/* <TableQuickFilter
                    value={quickFilter}
                    onFilterChange={handleQuickFilterChange}
                    quickFilterOptions={quickFilterOptions}
                /> */}
                <Table<DataProductSettingContract>
                    // onRow={(record) => {
                    //     return {
                    //         onClick: () => navigateToDataProduct(record.id),
                    //     };
                    // }}
                    components={components}
                    className={styles.table}
                    columns={editableColumns}
                    dataSource={dataProductSettings}
                    onChange={onChange}
                    pagination={pagination}
                    rowKey={(record) => record.id}
                    loading={isFetching}
                    rowHoverable
//                    rowClassName={styles.row}
                    rowClassName={() => 'editable-row'}
                    size={'small'}
                />
            </Flex>
            {isVisible && <CreateSettingModal onClose={handleClose} isOpen={isVisible} />}
        </Flex>
    );
}
