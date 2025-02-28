import styles from './general-tab.module.scss';
import { useTranslation } from 'react-i18next';
import { GeneralSettingsForm } from '../components/general-form/general-form.component';

export function GeneralTab() {
    const { t } = useTranslation();
    return (
        <div>
            <GeneralSettingsForm />
        </div>
    );
}
