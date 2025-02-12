import { Flex } from 'antd';
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

export function TagsTable() {
    const { t } = useTranslation();
    const { data: tags = [], isFetching } = useGetAllTagsQuery();
    const { pagination, handlePaginationChange } = useTablePagination({});
    const [editTag, { isLoading: isEditing }] = useUpdateTagMutation();
    const [onRemoveTag, { isLoading: isRemoving }] = useRemoveTagMutation();

    const columns = getTagsTableColums({ t, onRemoveTag });

    const onChange: TableProps<TagContract>['onChange'] = (pagination) => {
        handlePaginationChange(pagination);
    };

    const handleSave = async (tag: TagContract) => {
        try {
            await editTag({ tag, tagId: tag.id });
            dispatchMessage({ content: t('Tag updated successfully'), type: 'success' });
        } catch (error) {
            dispatchMessage({ content: t('Could not update tag'), type: 'error' });
        }
    };

    return (
        <Flex vertical className={styles.tableContainer}>
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
        </Flex>
    );
}
