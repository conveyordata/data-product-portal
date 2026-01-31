import type { EventContract } from '../events/event.contract';
import type { UserContract } from '../users';

export interface NotificationContract {
    id: string;
    user_id: string;
    user: UserContract;
    event_id: string;
    event: EventContract;
}
