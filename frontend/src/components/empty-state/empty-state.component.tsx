import { SearchOutlined } from '@ant-design/icons';
import { Flex, Typography, theme } from 'antd';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';
import styles from './empty-state.module.scss';

const { Title, Paragraph } = Typography;

type Props = {
    /** Icon of the thing that is missing, so the state is recognisable at a glance. */
    icon: ReactNode;
    title: string;
    description?: ReactNode;
    /** Shown only when nothing exists yet. A filtered list offers no action to take. */
    action?: ReactNode;
    /** Active search term. When set, the "nothing matched" variant is shown instead. */
    searchTerm?: string;
    /** Plural noun for the no-results copy, e.g. "Data Products". Required alongside searchTerm. */
    subject?: string;
};

export function EmptyState({ icon, title, description, action, searchTerm, subject }: Props) {
    const { t } = useTranslation();
    const {
        token: { colorPrimary, colorPrimaryBg },
    } = theme.useToken();
    const isFiltered = Boolean(searchTerm?.trim());

    return (
        <Flex vertical align="center" className={styles.container}>
            <div className={styles.tile} style={{ backgroundColor: colorPrimaryBg, color: colorPrimary }}>
                {isFiltered ? <SearchOutlined /> : icon}
            </div>
            <Title level={5} className={styles.title}>
                {isFiltered ? t('No {{subject}} match "{{searchTerm}}"', { subject, searchTerm }) : title}
            </Title>
            {(isFiltered || description) && (
                <Paragraph type="secondary" className={styles.description}>
                    {isFiltered
                        ? t('Check the spelling, or clear the search to see all {{subject}}.', { subject })
                        : description}
                </Paragraph>
            )}
            {!isFiltered && action && <div className={styles.action}>{action}</div>}
        </Flex>
    );
}
