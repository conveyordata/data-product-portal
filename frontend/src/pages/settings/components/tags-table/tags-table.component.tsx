import { Button, Flex, Space, Typography } from 'antd';
import styles from './tags-table.module.scss';
import { useTranslation } from 'react-i18next';
import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
import { TagContract } from '@/types/tag/tag.ts';
import {
    useGetAllTagsQuery,
    useRemoveTagMutation,
    useUpdateTagMutation,
} from '@/store/features/tags/tags-api-slice.tsx';
import { TableProps } from 'antd/lib';
import { useTablePagination } from '@/hooks/use-table-pagination';
import { EditableTable } from '@/components/editable-table/editable-table.component';
import { getTagsTableColums } from './tags-table-columns';
import { useModal } from '@/hooks/use-modal';
import { CreateTagsModal } from './tags-form-modal.component';
import { useState } from 'react';

export function TagsTable() {
    const { t } = useTranslation();
    const { data: tags = [], isFetching } = useGetAllTagsQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const { isVisible, handleOpen, handleClose } = useModal();
    const [editTag, { isLoading: isEditing }] = useUpdateTagMutation();
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

    const handleSave = async (tag: TagContract) => {
        try {
            await editTag({ tag, tagId: tag.id });
            dispatchMessage({ content: t('Tag updated successfully'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Could not update tag'), type: 'error' });
        }
    };

    const columns = getTagsTableColums({ t, onRemoveTag, handleEdit });

    return (
        <Flex vertical className={styles.tableContainer}>
            <Flex className={styles.searchContainer}>
                <Typography.Title level={3}>{t('Tags')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Tag')}
                    </Button>
                </Space>
            </Flex>
            <Flex vertical className={styles.tableFilters}>
                <EditableTable<TagContract>
                    data={tags}
                    columns={columns}
                    handleSave={handleSave}
                    onChange={onChange}
                    pagination={pagination}
                    rowKey={(record) => record.id}
                    loading={isFetching}
                    rowHoverable
                    rowClassName={() => 'editable-row'}
                    size={'small'}
                />
            </Flex>
            {isVisible && (
                <CreateTagsModal onClose={handleClose} t={t} isOpen={isVisible} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
