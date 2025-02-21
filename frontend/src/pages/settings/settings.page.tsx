import styles from './settings.module.scss';
import { SettingsTabs } from './components/settings-tabs/settings-tabs.component.tsx';

export function Settings() {
    return (
        <div className={styles.container}>
            <SettingsTabs />
        </div>
    );
}
