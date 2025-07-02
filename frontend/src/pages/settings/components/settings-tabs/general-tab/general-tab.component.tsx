import { ThemeSettingsForm } from '../components/theme-form/theme-form.component';
import { DataTracking } from '../components/data-tracking/data-tracking.component';

export function GeneralTab() {
    return (
        <div>
            <div>
                <ThemeSettingsForm />
            </div>
            <div>
                <DataTracking />
            </div>
        </div>
    );
}
