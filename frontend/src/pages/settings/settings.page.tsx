import { SettingsTabs } from './components/settings-tabs/settings-tabs.component.tsx';
import styles from './settings.module.scss';

export function Settings() {
    return (
        <div className={styles.container}>
            <SettingsTabs />
        </div>
    );
}
