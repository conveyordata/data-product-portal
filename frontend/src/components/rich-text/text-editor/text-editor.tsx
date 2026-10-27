import { CloseOutlined, EditOutlined, SaveOutlined } from '@ant-design/icons';
import { Table } from '@tiptap/extension-table';
import { TableCell } from '@tiptap/extension-table-cell';
import { TableHeader } from '@tiptap/extension-table-header';
import { TableRow } from '@tiptap/extension-table-row';
import { Typography } from '@tiptap/extension-typography';
import { EditorContent, useEditor } from '@tiptap/react';
import { StarterKit } from '@tiptap/starter-kit';
import { Button, Flex, Popconfirm, Tooltip } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { TextStyleCustomExtension } from '@/components/rich-text/extensions/text-style/text-style-custom-extension.tsx';
import { TextEditorMenu } from '@/components/rich-text/text-editor-menu/text-editor-menu.tsx';

import styles from './text-editor.module.scss';

type Props = {
    initialContent?: string | null;
    isDisabled?: boolean;
    onSubmit?: (content: string) => Promise<void>;
    isSubmitting?: boolean;
    isLoading?: boolean;
};

const extensions = [StarterKit, Typography, TextStyleCustomExtension, Table, TableCell, TableHeader, TableRow];

export const TextEditor = ({
    initialContent,
    onSubmit,
    isDisabled,
    isLoading = false,
    isSubmitting = false,
}: Props) => {
    const { t } = useTranslation();
    const [content, setContent] = useState(initialContent);
    const [savedContent, setSavedContent] = useState(initialContent);
    const [isEditMode, setIsEditMode] = useState(false);
    const isDirty = content !== savedContent;
    const editor = useEditor({
        extensions,
        // Compare against the editor's own HTML: it normalises the stored content, e.g. a blank page to <p></p>.
        onCreate: ({ editor }) => {
            setContent(editor.getHTML());
            setSavedContent(editor.getHTML());
        },
        onUpdate: ({ editor }) => {
            setContent(editor.getHTML());
        },
        editorProps: {
            attributes: {
                class: styles.editor,
            },
        },
        content,
        editable: false,
    });

    async function handleSubmit() {
        const html = editor?.getHTML();
        if (!onSubmit || !html) {
            return;
        }
        try {
            await onSubmit(html);
            setSavedContent(html);
            setIsEditMode(false);
        } catch {
            // The caller reports the failure; staying in edit mode keeps the text.
        }
    }

    function handleDiscard() {
        editor?.commands.setContent(savedContent ?? '');
        setContent(savedContent);
        setIsEditMode(false);
    }

    useEffect(() => {
        editor?.setEditable(isEditMode && !isDisabled);
    }, [isEditMode, isDisabled, editor]);

    if (!editor) {
        return null;
    }

    return (
        <div className={styles.editorContainer}>
            {isEditMode && <TextEditorMenu editor={editor} isDisabled={isDisabled} />}
            <div className={styles.editorContent}>
                <EditorContent editor={editor} content={content ?? undefined} className={styles.content} />
            </div>
            <Flex gap="small" justify="flex-end" className={styles.actions}>
                {isEditMode ? (
                    <>
                        <Popconfirm
                            title={t('Discard changes?')}
                            description={t('Your unsaved changes will be lost.')}
                            okText={t('Discard')}
                            cancelText={t('Keep editing')}
                            onConfirm={handleDiscard}
                            disabled={!isDirty}
                        >
                            <Tooltip title={t('Discard changes')}>
                                <Button
                                    shape="circle"
                                    aria-label={t('Discard changes')}
                                    onClick={isDirty ? undefined : handleDiscard}
                                    icon={<CloseOutlined />}
                                    disabled={isLoading || isSubmitting}
                                />
                            </Tooltip>
                        </Popconfirm>
                        <Tooltip title={t('Save changes')}>
                            <Button
                                type="primary"
                                shape="circle"
                                aria-label={t('Save changes')}
                                onClick={handleSubmit}
                                icon={<SaveOutlined />}
                                disabled={isDisabled || isLoading || isSubmitting}
                                loading={isSubmitting}
                            />
                        </Tooltip>
                    </>
                ) : (
                    !isDisabled && (
                        <Tooltip title={t('Edit content')}>
                            <Button
                                type="primary"
                                shape="circle"
                                aria-label={t('Edit content')}
                                onClick={() => setIsEditMode(true)}
                                icon={<EditOutlined />}
                                disabled={isLoading || isSubmitting}
                            />
                        </Tooltip>
                    )
                )}
            </Flex>
        </div>
    );
};
