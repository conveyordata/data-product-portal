import { Button, Flex, Space, Table, Typography } from 'antd';
import styles from './tags-table.module.scss';
import { useTranslation } from 'react-i18next';
import { TagContract } from '@/types/tag/tag.ts';
import { useGetAllTagsQuery, useRemoveTagMutation } from '@/store/features/tags/tags-api-slice.tsx';
import { TableProps } from 'antd/lib';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { getTagsTableColums } from './tags-table-columns';
import { useModal } from '@/hooks/use-modal';
import { CreateTagsModal } from './tags-form-modal.component';
import { useState } from 'react';

export function TagsTable() {
    const { t } = useTranslation();
    const { data: tags = [], isFetching } = useGetAllTagsQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();
    const [onRemoveTag] = useRemoveTagMutation();
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

    const columns = getTagsTableColums({ t, onRemoveTag, handleEdit });

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
                loading={isFetching}
                rowHoverable
                rowClassName={() => 'editable-row'}
                size={'small'}
            />
            {isVisible && (
                <CreateTagsModal onClose={handleClose} t={t} isOpen={isVisible} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
