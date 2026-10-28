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
import { type ChainedCommands, type Editor, useEditorState } from '@tiptap/react';
import { Button, Divider, Flex, Select, Tooltip } from 'antd';
import { Fragment, type ReactNode } from 'react';
import { useTranslation } from 'react-i18next';

import styles from './text-editor-menu.module.scss';

type Props = {
    editor: Editor;
    isDisabled?: boolean;
};

type MenuButton = {
    label: string;
    icon: ReactNode;
    run: (chain: ChainedCommands) => ChainedCommands;
    active?: boolean;
    disabled?: boolean;
};

const headingLevels = [1, 2, 3] as const;

export const TextEditorMenu = ({ editor, isDisabled }: Props) => {
    const { t } = useTranslation();
    const state = useEditorState({
        editor,
        selector: ({ editor }) => ({
            canUndo: editor.can().undo(),
            canRedo: editor.can().redo(),
            headingLevel: headingLevels.find((level) => editor.isActive('heading', { level })),
            bold: editor.isActive('bold'),
            underline: editor.isActive('underline'),
            italic: editor.isActive('italic'),
            strike: editor.isActive('strike'),
            bulletList: editor.isActive('bulletList'),
            orderedList: editor.isActive('orderedList'),
            codeBlock: editor.isActive('codeBlock'),
        }),
    });

    const [history, ...formatting]: MenuButton[][] = [
        [
            { label: t('Undo'), icon: <UndoOutlined />, run: (c) => c.undo(), disabled: !state.canUndo },
            { label: t('Redo'), icon: <RedoOutlined />, run: (c) => c.redo(), disabled: !state.canRedo },
        ],
        [
            { label: t('Bold'), icon: <BoldOutlined />, run: (c) => c.toggleBold(), active: state.bold },
            {
                label: t('Underline'),
                icon: <UnderlineOutlined />,
                run: (c) => c.toggleUnderline(),
                active: state.underline,
            },
            { label: t('Italic'), icon: <ItalicOutlined />, run: (c) => c.toggleItalic(), active: state.italic },
            { label: t('Strike'), icon: <StrikethroughOutlined />, run: (c) => c.toggleStrike(), active: state.strike },
        ],
        [
            {
                label: t('Bulleted list'),
                icon: <UnorderedListOutlined />,
                run: (c) => c.toggleBulletList(),
                active: state.bulletList,
            },
            {
                label: t('Numbered list'),
                icon: <OrderedListOutlined />,
                run: (c) => c.toggleOrderedList(),
                active: state.orderedList,
            },
        ],
        [
            {
                label: t('Code block'),
                icon: <CodeOutlined />,
                run: (c) => c.toggleCodeBlock(),
                active: state.codeBlock,
            },
        ],
    ];

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
        <Flex align="center">
            <Popover content={t('Undo')} trigger="hover">
                <Button className={getClassName('undo')} onClick={undo} disabled={!canUndo || isDisabled} type="text">
                    <UndoOutlined />
                </Button>
            </Popover>
            <Popover content={t('Redo')} trigger="hover">
                <Button className={getClassName('redo')} onClick={redo} disabled={!canRedo || isDisabled} type="text">
                    <RedoOutlined />
                </Button>
            </Popover>
            <Divider type="vertical" />
            <Popover content={t('Turn into')} trigger="hover">
                <div>
                    <Select
                        options={[
                            {
                                label: t('Turn into'),
                                options: TextTypeMenuOptions.map((option) => ({ ...option, key: option.value })),
                            },
                        ]}
                        defaultValue="paragraph"
                        className={styles.textTypeDropdown}
                        title={t('Turn into')}
                        value={getActiveTextType()}
                        onChange={onTextTypeChange}
                        disabled={isDisabled}
                    />
                </div>
            </Popover>
            <Divider type="vertical" />
            <Popover content={t('Bold')} trigger="hover">
                <Button className={getClassName('bold')} onClick={toggleBold} disabled={isDisabled} type="text">
                    <BoldOutlined />
                </Button>
            </Popover>
            <Popover content={t('Underline')} trigger="hover">
                <Button
                    className={getClassName('underline')}
                    onClick={toggleUnderline}
                    disabled={isDisabled}
                    type="text"
                >
                    <UnderlineOutlined />
                </Button>
            </Popover>
            <Popover content={t('Italic')} trigger="hover">
                <Button className={getClassName('italic')} onClick={toggleItalic} disabled={isDisabled} type="text">
                    <ItalicOutlined />
                </Button>
            </Popover>
            <Popover content={t('Strike')} trigger="hover">
                <Button className={getClassName('strike')} onClick={toggleStrike} disabled={isDisabled} type="text">
                    <StrikethroughOutlined />
                </Button>
            </Popover>
            <Divider type="vertical" />
            <Popover content={t('Bulleted list')} trigger="hover">
                <Button
                    onClick={() => toggleBulletList()}
                    className={getClassName('bulletList')}
                    disabled={isDisabled}
                    type="text"
                >
                    <UnorderedListOutlined />
                </Button>
            </Popover>
            <Popover content={t('Numbered list')} trigger="hover">
                <Button
                    onClick={() => toggleOrderedList()}
                    className={getClassName('orderedList')}
                    disabled={isDisabled}
                    type="text"
                >
                    <OrderedListOutlined />
                </Button>
            </Popover>
            <Divider type="vertical" />
            <Popover content={t('Code block')} trigger="hover">
                <Button className={getClassName('codeBlock')} onClick={toggleCode} disabled={isDisabled} type="text">
                    <CodeOutlined />
                </Button>
            </Popover>
        </Flex>
    const renderButtons = (buttons: MenuButton[]) =>
        buttons.map(({ label, icon, run, active, disabled }) => (
            <Tooltip key={label} title={label}>
                <Button
                    aria-label={label}
                    icon={icon}
                    type={active ? 'primary' : 'text'}
                    disabled={disabled || isDisabled}
                    onClick={() => run(editor.chain().focus()).run()}
                />
            </Tooltip>
        ));

    return (
        <Flex align="center" className={styles.menuBar}>
            {renderButtons(history)}
            <Divider orientation="vertical" />
            <Tooltip title={t('Turn into')}>
                <Select
                    aria-label={t('Turn into')}
                    options={[
                        { label: t('Text'), value: 0 },
                        ...headingLevels.map((level) => ({
                            label: t('Heading {{value}}', { value: level }),
                            value: level,
                        })),
                    ]}
                    className={styles.textTypeDropdown}
                    value={state.headingLevel ?? 0}
                    onChange={(level: Level | 0) => {
                        const chain = editor.chain().focus();
                        (level ? chain.setHeading({ level }) : chain.setParagraph()).run();
                    }}
                    disabled={isDisabled}
                />
            </Tooltip>
            {formatting.map((buttons) => (
                <Fragment key={buttons[0].label}>
                    <Divider orientation="vertical" />
                    {renderButtons(buttons)}
                </Fragment>
            ))}
        </Flex>
    );
};
