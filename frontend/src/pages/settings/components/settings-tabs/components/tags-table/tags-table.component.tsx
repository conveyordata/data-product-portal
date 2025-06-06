import { Button, Flex, Space, Table, Typography } from 'antd';
import type { TableProps } from 'antd/lib';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { useGetAllTagsQuery, useRemoveTagMutation } from '@/store/features/tags/tags-api-slice';
import type { TagContract } from '@/types/tag/tag';

import { CreateTagsModal } from './tags-form-modal.component';
import { getTagsTableColumns } from './tags-table-columns';
import styles from './tags-table.module.scss';

export function TagsTable() {
    const { t } = useTranslation();
    const { data: tags = [], isFetching } = useGetAllTagsQuery();
    const { pagination, handlePaginationChange } = useTablePagination(tags);
    const { isVisible, handleOpen, handleClose } = useModal();
    const [onRemoveTag, { isLoading: isRemoving }] = useRemoveTagMutation();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<TagContract | undefined>(undefined);

    const onChange: TableProps<TagContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleAdd = () => {
        setMode('create');
        setInitial(undefined);
        handleOpen();
    };

    const handleEdit = (tag: TagContract) => () => {
        setMode('edit');
        setInitial(tag);
        handleOpen();
    };

    const columns = getTagsTableColumns({ t, onRemoveTag, handleEdit });

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.addContainer}>
                <Typography.Title level={3}>{t('Tags')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Tag')}
                    </Button>
                </Space>
            </Flex>
            <Table<TagContract>
                dataSource={tags}
                columns={columns}
                onChange={onChange}
                pagination={pagination}
                rowKey={(record) => record.id}
                loading={isFetching || isRemoving}
                rowHoverable
                rowClassName={() => 'editable-row'}
                size={'small'}
            />
            {isVisible && initial && (
                <CreateTagsModal isOpen={isVisible} onClose={handleClose} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
