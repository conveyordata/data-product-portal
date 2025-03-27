import { Handle, type HandleProps } from '@xyflow/react';

import styles from './default-handle.module.scss';

export const DefaultHandle = ({ id, position, type, ...props }: HandleProps) => {
    return <Handle id={id} type={type} position={position} className={styles.handle} {...props} />;
};
