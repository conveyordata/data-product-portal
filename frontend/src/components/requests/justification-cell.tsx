import { ExclamationCircleOutlined } from '@ant-design/icons';
import { Tooltip, Typography } from 'antd';
import { useTranslation } from 'react-i18next';

type Props = {
    justification?: string;
};

const MIN_JUSTIFICATION_LENGTH = 10;
const PREVIEW_LENGTH = 50;

export function JustificationCell({ justification }: Props) {
    const { t } = useTranslation();

    if (!justification || justification.trim().length === 0) {
        return (
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <Tooltip title={t('No business justification provided')}>
                    <ExclamationCircleOutlined style={{ color: '#ff4d4f', fontSize: 16 }} />
                </Tooltip>
                <Typography.Text type="secondary" italic>
                    {t('No justification')}
                </Typography.Text>
            </div>
        );
    }

    const trimmedJustification = justification.trim();
    const isTooShort = trimmedJustification.length < MIN_JUSTIFICATION_LENGTH;
    const preview =
        trimmedJustification.length > PREVIEW_LENGTH
            ? `${trimmedJustification.substring(0, PREVIEW_LENGTH)}...`
            : trimmedJustification;

    return (
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
            {isTooShort && (
                <Tooltip title={t('Justification may be too brief for a meaningful review')}>
                    <ExclamationCircleOutlined style={{ color: '#faad14', fontSize: 16, marginTop: 2 }} />
                </Tooltip>
            )}
            <Tooltip title={trimmedJustification} placement="topLeft">
                <Typography.Text
                    style={{
                        maxWidth: 350,
                        display: 'block',
                        cursor: 'help',
                    }}
                >
                    {preview}
                </Typography.Text>
            </Tooltip>
        </div>
    );
}
