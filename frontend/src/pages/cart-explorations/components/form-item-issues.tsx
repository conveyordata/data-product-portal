import { Alert } from 'antd';
import { t } from 'i18next';

type Props = {
    submitFormIssues: { key: string; value: string }[];
};

export const FormIssues = ({ submitFormIssues }: Props) => {
    if (!submitFormIssues.length) {
        return null;
    }
    return (
        <Alert
            title={t('Cannot submit request')}
            description={
                <ul style={{ margin: 0, paddingLeft: 20 }}>
                    {submitFormIssues.map((reason) => (
                        <li key={reason.key}>{reason.value}</li>
                    ))}
                </ul>
            }
            type="warning"
            showIcon
            style={{ marginBottom: 16 }}
        />
    );
};
