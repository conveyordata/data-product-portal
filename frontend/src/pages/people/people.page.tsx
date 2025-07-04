import { PeopleTable } from '@/pages/people/components/people-table/people-table.component';
import styles from './people.module.scss';

export function People() {
    return (
        <div className={styles.container}>
            <PeopleTable />
        </div>
    );
}
