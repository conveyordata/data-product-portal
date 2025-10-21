import { ShoppingCartOutlined } from '@ant-design/icons';
import { Badge, Button, Flex, List, Popover } from 'antd';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import styles from '@/components/layout/navbar/cli-download/cli-download-button.module.scss';
import { ApplicationPaths } from '@/types/navigation.ts';

const ShoppingCartItems = () => {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const data = [
        'Data product A - output port A',
        'Data product A - output port B',
        'Data product B - output port A',
        'Data product C - output port A',
    ];

    return (
        <List
            header={<div>Current items</div>}
            footer={
                <Flex justify={'flex-end'}>
                    <Button
                        className={styles.formButton}
                        type="primary"
                        onClick={() => {
                            navigate(ApplicationPaths.MarketplaceCart);
                        }}
                    >
                        {t('Checkout')}{' '}
                    </Button>
                </Flex>
            }
            bordered
            dataSource={data}
            renderItem={(item) => <List.Item>{item}</List.Item>}
        />
    );
};

export const CartButton = () => {
    return (
        <Popover content={<ShoppingCartItems />} trigger={'hover'} placement="bottom">
            <Badge count={5}>
                <Button shape={'circle'} className={styles.iconButton} icon={<ShoppingCartOutlined />} />
            </Badge>
        </Popover>
    );
};
