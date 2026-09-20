import { CloseOutlined, EditOutlined, SaveOutlined } from '@ant-design/icons';
import { Table } from '@tiptap/extension-table';
import { TableCell } from '@tiptap/extension-table-cell';
import { TableHeader } from '@tiptap/extension-table-header';
import { TableRow } from '@tiptap/extension-table-row';
import { Typography } from '@tiptap/extension-typography';
import { EditorContent, useEditor } from '@tiptap/react';
import { StarterKit } from '@tiptap/starter-kit';
import { Button, Flex, Popconfirm, Tooltip } from 'antd';
import clsx from 'clsx';
import { useEffect, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { TextStyleCustomExtension } from '@/components/rich-text/extensions/text-style/text-style-custom-extension.tsx';
import { TextEditorMenu } from '@/components/rich-text/text-editor-menu/text-editor-menu.tsx';

import styles from './text-editor.module.scss';

type Props = {
    initialContent?: string | null;
    isDisabled?: boolean;
    /** Rejecting keeps the editor open so the author does not lose their text. */
    onSubmit?: (content: string) => void | Promise<void>;
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
    const contentRef = useRef<HTMLDivElement>(null);
    const isEditable = isEditMode && !isDisabled;
    const isDirty = content !== savedContent;
    const editor = useEditor({
        extensions,
        onUpdate: ({ editor }) => {
            setContent(editor.getHTML());
        },
        editorProps: {
            attributes: {
                class: styles.editor,
            },
        },
        content,
        editable: isEditMode,
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
            // The caller reports the failure. Stay in edit mode so the text survives.
        }
    }

    function handleCancel() {
        editor?.commands.setContent(savedContent ?? '');
        setContent(savedContent);
        setIsEditMode(false);
    }

    useEffect(() => {
        if (isDisabled) {
            editor?.setEditable(false);
        } else {
            editor?.setEditable(isEditMode);
        }
    }, [isEditMode, isDisabled, editor]);

    useEffect(() => {
        const container = contentRef.current;
        if (!container || !editor || !isEditable) {
            return;
        }
        const focusEditor = (event: globalThis.MouseEvent) => {
            if (!editor.view.dom.contains(event.target as globalThis.Node)) {
                editor.commands.focus('end');
            }
        };
        container.addEventListener('mousedown', focusEditor);
        return () => container.removeEventListener('mousedown', focusEditor);
    }, [editor, isEditable]);

    if (!editor) {
        return null;
    }

    return (
        <div className={styles.editorContainer}>
            {isEditMode && <TextEditorMenu editor={editor} isDisabled={isDisabled} />}
            <div ref={contentRef} className={clsx(styles.editorContent, isEditable && styles.editorContentEditable)}>
                <EditorContent editor={editor} content={content ?? undefined} className={styles.content} />
            </div>
            <Flex gap="small" justify="flex-end" align="center" className={styles.actions}>
                {isEditMode ? (
                    <>
                        <Popconfirm
                            title={t('Discard changes?')}
                            description={t('The edits you made to this page will be lost.')}
                            okText={t('Discard')}
                            cancelText={t('Keep editing')}
                            onConfirm={handleCancel}
                            disabled={!isDirty}
                        >
                            <Tooltip title={t('Discard changes')}>
                                <Button
                                    shape="circle"
                                    aria-label={t('Discard changes')}
                                    onClick={isDirty ? undefined : handleCancel}
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
