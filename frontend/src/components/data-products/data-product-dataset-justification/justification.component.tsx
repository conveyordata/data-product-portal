import { Typography } from 'antd';
import { useTranslation } from 'react-i18next';

type Props = {
    justification: string;
};
export default function Justification({ justification }: Props) {
    const { t } = useTranslation();
    return (
        <Typography.Paragraph
            style={{ whiteSpace: 'pre-wrap', color: 'inherit', marginBottom: 0 }}
            ellipsis={{
                rows: 5,
                expandable: true,
                symbol: t('more'),
                onExpand: (e) => e.stopPropagation(),
            }}
        >
            {justification}
        </Typography.Paragraph>
    );
}
