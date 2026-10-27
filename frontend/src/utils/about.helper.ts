import type { TFunction } from 'i18next';
import { dispatchMessage } from '@/utils/feedback.ts';

export async function saveAbout(update: Promise<unknown>, t: TFunction): Promise<void> {
    try {
        await update;
    } catch (error) {
        dispatchMessage({ content: t('Could not update about section'), type: 'error' });
        throw error;
    }
    dispatchMessage({ content: t('About section successfully updated'), type: 'success' });
}
