import { CheckOutlined, EditOutlined } from '@ant-design/icons';
import Link from '@tiptap/extension-link';
import Table from '@tiptap/extension-table';
import TableCell from '@tiptap/extension-table-cell';
import TableHeader from '@tiptap/extension-table-header';
import TableRow from '@tiptap/extension-table-row';
import Typography from '@tiptap/extension-typography';
import Underline from '@tiptap/extension-underline';
import { EditorContent, useEditor } from '@tiptap/react';
import { StarterKit } from '@tiptap/starter-kit';
import { Button, Popover } from 'antd';
import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { TextStyleCustomExtension } from '@/components/rich-text/extensions/text-style/text-style-custom-extension.tsx';
import { TextEditorMenu } from '@/components/rich-text/text-editor-menu/text-editor-menu.tsx';

import styles from './text-editor.module.scss';

type Props = {
    initialContent?: string;
    isDisabled?: boolean;
    onSubmit?: (content: string) => void;
    isSubmitting?: boolean;
    isLoading?: boolean;
    isInitialEditMode?: boolean;
};

const extensions = [
    StarterKit,
    Link.configure({
        autolink: true,
    }),
    Underline,
    Typography,
    TextStyleCustomExtension,
    Table,
    TableCell,
    TableHeader,
    TableRow,
];

export const TextEditor = ({
    initialContent,
    onSubmit,
    isDisabled,
    isLoading = false,
    isSubmitting = false,
    isInitialEditMode = false,
}: Props) => {
    const { t } = useTranslation();
    const [content, setContent] = useState(initialContent);
    const [isEditMode, setIsEditMode] = useState(isInitialEditMode && !isDisabled);
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

    function handleSubmit() {
        const html = editor?.getHTML();
        if (onSubmit && html) {
            onSubmit(html);
        }
    }

    function toggleEditMode() {
        setIsEditMode((prev) => !prev);
    }

    useEffect(() => {
        if (isDisabled) {
            editor?.setEditable(false);
        } else if (isEditMode) {
            editor?.setEditable(isEditMode);
        }
    }, [isEditMode, isDisabled, editor]);

    if (!editor) {
        return null;
    }

    return (
        <div className={styles.editorContainer}>
            {isEditMode && <TextEditorMenu editor={editor} isDisabled={isDisabled} />}
            <div className={styles.editorContent}>
                <EditorContent editor={editor} content={content} className={styles.content} />
            </div>
            {isEditMode ? (
                <Popover content={t('Save changes')}>
                    <Button
                        type="primary"
                        className={styles.submitButton}
                        onClick={handleSubmit}
                        icon={<CheckOutlined />}
                        disabled={isDisabled || isLoading || isSubmitting}
                        loading={isSubmitting}
                    />
                </Popover>
            ) : (
                !isDisabled && (
                    <Popover content={t('Edit content')}>
                        <Button
                            type="primary"
                            className={styles.submitButton}
                            onClick={toggleEditMode}
                            disabled={isDisabled || isLoading || isSubmitting}
                            icon={<EditOutlined />}
                        />
                    </Popover>
                )
            )}
        </div>
    );
};
