import {
    BoldOutlined,
    CodeOutlined,
    ItalicOutlined,
    OrderedListOutlined,
    RedoOutlined,
    StrikethroughOutlined,
    UnderlineOutlined,
    UndoOutlined,
    UnorderedListOutlined,
} from '@ant-design/icons';
import type { Level } from '@tiptap/extension-heading';
import type { Editor } from '@tiptap/react';
import { Button, Divider, Flex, Popover, Select, type SelectProps } from 'antd';
import clsx from 'clsx';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import styles from './text-editor-menu.module.scss';

type Props = {
    editor: Editor;
    isDisabled?: boolean;
};
export const TextEditorMenu = ({ editor, isDisabled }: Props) => {
    const { t } = useTranslation();

    const TextTypeMenuOptions: SelectProps['options'] = useMemo(
        () => [
            { label: t('Text'), value: 'paragraph' },
            { label: t('Heading {{value}}', { value: 1 }), value: 'heading1' },
            { label: t('Heading {{value}}', { value: 2 }), value: 'heading2' },
            { label: t('Heading {{value}}', { value: 3 }), value: 'heading3' },
        ],
        [t],
    );

    const toggleBold = useCallback(() => {
        editor?.chain().focus().toggleBold().run();
    }, [editor]);

    const toggleUnderline = useCallback(() => {
        editor?.chain().focus()?.toggleUnderline().run();
    }, [editor]);

    const toggleItalic = useCallback(() => {
        editor?.chain().focus().toggleItalic().run();
    }, [editor]);

    const toggleStrike = useCallback(() => {
        editor?.chain().focus().toggleStrike().run();
    }, [editor]);

    const toggleCode = useCallback(() => {
        editor?.chain().focus().toggleCodeBlock().run();
    }, [editor]);

    const undo = useCallback(() => {
        editor?.chain().focus().undo().run();
    }, [editor]);

    const redo = useCallback(() => {
        editor?.chain().focus().redo().run();
    }, [editor]);

    const toggleParagraph = useCallback(() => {
        editor?.chain().focus().setParagraph().run();
    }, [editor]);

    const toggleHeading = useCallback(
        (level: Level) => {
            editor?.chain().focus().toggleHeading({ level }).run();
        },
        [editor],
    );

    const toggleBulletList = useCallback(() => {
        editor?.chain().focus().toggleBulletList().run();
    }, [editor]);

    const toggleOrderedList = useCallback(() => {
        editor?.chain().focus().toggleOrderedList().run();
    }, [editor]);

    const canUndo = editor?.can().undo();
    const canRedo = editor?.can().redo();

    const getClassName = useCallback(
        (type: string, attributes?: Record<string, unknown>) => {
            return clsx(styles.menuButton, {
                [styles.active]: editor?.isActive(type, attributes),
            });
        },
        [editor],
    );

    function getActiveTextType() {
        if (editor?.isActive('heading', { level: 1 })) {
            return 'heading1';
        }
        if (editor?.isActive('heading', { level: 2 })) {
            return 'heading2';
        }
        if (editor?.isActive('heading', { level: 3 })) {
            return 'heading3';
        }
        return 'paragraph';
    }

    function onTextTypeChange(value: string) {
        switch (value) {
            case 'heading1':
                toggleHeading(1);
                break;
            case 'heading2':
                toggleHeading(2);
                break;
            case 'heading3':
                toggleHeading(3);
                break;
            case 'heading4':
                toggleHeading(4);
                break;
            case 'paragraph':
                toggleParagraph();
                break;
        }
    }

    if (!editor) {
        return null;
    }

    return (
        <div className={styles.menuBar}>
            <Flex className={styles.actionsContainer}>
                <Popover content={t('Undo')} trigger={'hover'}>
                    <Button
                        className={getClassName('undo')}
                        onClick={undo}
                        disabled={!canUndo || isDisabled}
                        type={'text'}
                    >
                        <UndoOutlined />
                    </Button>
                </Popover>
                <Popover content={t('Redo')} trigger={'hover'}>
                    <Button
                        className={getClassName('redo')}
                        onClick={redo}
                        disabled={!canRedo || isDisabled}
                        type={'text'}
                    >
                        <RedoOutlined />
                    </Button>
                </Popover>
                <Divider type={'vertical'} />
                <Popover content={t('Turn into')} trigger={'hover'}>
                    <div>
                        <Select
                            options={[
                                {
                                    label: t('Turn into'),
                                    options: TextTypeMenuOptions.map((option) => ({ ...option, key: option.value })),
                                },
                            ]}
                            defaultValue={'paragraph'}
                            className={styles.textTypeDropdown}
                            title={t('Turn into')}
                            value={getActiveTextType()}
                            onChange={onTextTypeChange}
                            disabled={isDisabled}
                        />
                    </div>
                </Popover>
                <Divider type={'vertical'} />
                <Popover content={t('Bold')} trigger={'hover'}>
                    <Button className={getClassName('bold')} onClick={toggleBold} disabled={isDisabled} type={'text'}>
                        <BoldOutlined />
                    </Button>
                </Popover>
                <Popover content={t('Underline')} trigger={'hover'}>
                    <Button
                        className={getClassName('underline')}
                        onClick={toggleUnderline}
                        disabled={isDisabled}
                        type={'text'}
                    >
                        <UnderlineOutlined />
                    </Button>
                </Popover>
                <Popover content={t('Italic')} trigger={'hover'}>
                    <Button
                        className={getClassName('italic')}
                        onClick={toggleItalic}
                        disabled={isDisabled}
                        type={'text'}
                    >
                        <ItalicOutlined />
                    </Button>
                </Popover>
                <Popover content={t('Strike')} trigger={'hover'}>
                    <Button
                        className={getClassName('strike')}
                        onClick={toggleStrike}
                        disabled={isDisabled}
                        type={'text'}
                    >
                        <StrikethroughOutlined />
                    </Button>
                </Popover>
                <Divider type={'vertical'} />
                <Popover content={t('Bulleted list')} trigger={'hover'}>
                    <Button
                        onClick={() => toggleBulletList()}
                        className={getClassName('bulletList')}
                        disabled={isDisabled}
                        type={'text'}
                    >
                        <UnorderedListOutlined />
                    </Button>
                </Popover>
                <Popover content={t('Numbered list')} trigger={'hover'}>
                    <Button
                        onClick={() => toggleOrderedList()}
                        className={getClassName('orderedList')}
                        disabled={isDisabled}
                        type={'text'}
                    >
                        <OrderedListOutlined />
                    </Button>
                </Popover>
                <Divider type={'vertical'} />
                <Popover content={t('Code block')} trigger={'hover'}>
                    <Button
                        className={getClassName('codeBlock')}
                        onClick={toggleCode}
                        disabled={isDisabled}
                        type={'text'}
                    >
                        <CodeOutlined />
                    </Button>
                </Popover>
            </Flex>
        </div>
    );
};
