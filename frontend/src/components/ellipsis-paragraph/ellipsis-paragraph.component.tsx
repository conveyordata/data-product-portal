import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

type Props = {
    text?: string | null;
};
export default function EllipsisParagraph({ text }: Props) {
    const { t } = useTranslation();
    return (
        <Typography.Paragraph
            style={{ whiteSpace: 'pre-wrap' }}
            ellipsis={{
                rows: 5,
                expandable: true,
                symbol: t('more'),
                onExpand: (e) => e.stopPropagation(),
            }}
        >
            {text}
        </Typography.Paragraph>
    );
}
