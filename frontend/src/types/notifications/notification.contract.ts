import type { EventContract } from '../events/event.contract';
import type { UserContract } from '../users';

export enum NotificationTypes {
    DataProductDatasetNotification = 'DataProductDatasetNotification',
    DataOutputDatasetNotification = 'DataOutputDatasetNotification',
    DataProductMembershipNotification = 'DataProductMembershipNotification',
}

export interface NotificationContract {
    id: string;
    user_id: string;
    user: UserContract;
    event_id: string;
    event: EventContract;
}
