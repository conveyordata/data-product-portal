// Common between explorer and full-explorer
import '@xyflow/react/dist/base.css';

import { Button } from 'antd';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router';

import { TabKeys as DataOutputTabKeys } from '@/pages/data-output/components/data-output-tabs/data-output-tabkeys';
import { TabKeys as DataProductTabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys';
import { TabKeys as DatasetTabKeys } from '@/pages/dataset/components/dataset-tabs/dataset-tabkeys';
import { createDataOutputIdPath, createDataProductIdPath, createDatasetIdPath } from '@/types/navigation.ts';

import styles from './explorer.module.scss';

function LinkToDataProductNode({ id }: { id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDataProductIdPath(id, DataProductTabKeys.Explorer)} className={styles.link}>
            <Button type="default">{t('View data product')}</Button>
        </Link>
    );
}

function LinkToDatasetNode({ id }: { id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDatasetIdPath(id, DatasetTabKeys.Explorer)} className={styles.link}>
            <Button type="default">{t('View dataset')}</Button>
        </Link>
    );
}

function LinkToDataOutputNode({ id, product_id }: { id: string; product_id: string }) {
    const { t } = useTranslation();
    return (
        <Link to={createDataOutputIdPath(id, product_id, DataOutputTabKeys.Explorer)} className={styles.link}>
            <Button type="default">{t('View data output')}</Button>
        </Link>
    );
}

export { LinkToDataOutputNode, LinkToDataProductNode, LinkToDatasetNode };
