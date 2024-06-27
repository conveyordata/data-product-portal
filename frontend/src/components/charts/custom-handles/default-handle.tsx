import { Handle, HandleProps } from 'reactflow';
import styles from './default-handle.module.scss';

export const DefaultHandle = ({ id, position, type, ...props }: HandleProps) => {
    return <Handle id={id} type={type} position={position} className={styles.handle} {...props} />;
};
