import { Button, Flex, Space, Table, Typography } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { useModal } from '@/hooks/use-modal';
import {
    type TagsGetItem,
    useGetTagsQuery,
    useRemoveTagMutation,
} from '@/store/api/services/generated/configurationTagsApi.ts';
import type { TagContract } from '@/types/tag/tag';
import { CreateTagsModal } from './tags-form-modal.component';
import styles from './tags-table.module.scss';
import { getTagsTableColumns } from './tags-table-columns';

export function TagsTable() {
    const { t } = useTranslation();
    const { data: tags, isFetching } = useGetTagsQuery();
    const { isVisible, handleOpen, handleClose } = useModal();
    const [onRemoveTag, { isLoading: isRemoving }] = useRemoveTagMutation();
    const [mode, setMode] = useState<'create' | 'edit'>('create');
    const [initial, setInitial] = useState<TagContract | undefined>(undefined);

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
        <Flex vertical gap={'large'}>
            <Flex justify={'space-between'} align={'center'}>
                <Typography.Title level={3}>{t('Tags')}</Typography.Title>
                <Space>
                    <Button className={styles.formButton} type={'primary'} onClick={handleAdd}>
                        {t('Add Tag')}
                    </Button>
                </Space>
            </Flex>
            <Table<TagsGetItem>
                dataSource={tags?.tags ?? []}
                columns={columns}
                rowKey={(record) => record.id}
                loading={isFetching || isRemoving}
                rowHoverable
                size={'small'}
            />
            {isVisible && (mode === 'create' || initial) && (
                <CreateTagsModal isOpen={isVisible} onClose={handleClose} mode={mode} initial={initial} />
            )}
        </Flex>
    );
}
