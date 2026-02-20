import { ShoppingCartOutlined } from '@ant-design/icons';
import { Badge, Button, Popover } from 'antd';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { Link } from 'react-router';
import styles from '@/components/layout/navbar/cli-download/cli-download-button.module.scss';
import { selectCartDatasetIds } from '@/store/features/cart/cart-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

export const CartButton = () => {
    const { t } = useTranslation();
    const cartDatasetIds = useSelector(selectCartDatasetIds);
    return (
        <Popover placement={'bottom'} content={t('Go to checkout')} color={'white'} trigger={'hover'}>
            <Badge count={cartDatasetIds?.length}>
                <Link to={ApplicationPaths.MarketplaceCart}>
                    <Button shape={'circle'} className={styles.iconButton} icon={<ShoppingCartOutlined />} />
                </Link>
            </Badge>
        </Popover>
    );
};
