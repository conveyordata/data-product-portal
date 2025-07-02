import { DataTracking } from '../components/data-tracking/data-tracking.component';
import { ThemeSettingsForm } from '../components/theme-form/theme-form.component';

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
