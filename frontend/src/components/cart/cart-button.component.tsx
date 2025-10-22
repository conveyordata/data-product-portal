import { ShoppingCartOutlined } from '@ant-design/icons';
import { Badge, Button, Descriptions, Flex, List, Popover, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import styles from '@/components/layout/navbar/cli-download/cli-download-button.module.scss';
import { cartData } from '@/store/test-data.tsx';
import { ApplicationPaths } from '@/types/navigation.ts';

const ShoppingCartItems = () => {
    const navigate = useNavigate();
    const { t } = useTranslation();

    return (
        <List
            header={<Typography.Title level={3}>Shopping cart</Typography.Title>}
            style={{ width: '400px' }}
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
            dataSource={cartData}
            renderItem={(item) => (
                <List.Item>
                    <Descriptions
                        title={item.outputPortName}
                        column={1}
                        items={[
                            {
                                key: 0,
                                label: <Typography.Text strong>Data product</Typography.Text>,
                                children: item.dataProductName,
                            },
                        ]}
                    />
                </List.Item>
            )}
        />
    );
};

export const CartButton = () => {
    return (
        <Popover content={<ShoppingCartItems />} trigger={'hover'} placement="bottom">
            <Badge count={cartData.length}>
                <Button shape={'circle'} className={styles.iconButton} icon={<ShoppingCartOutlined />} />
            </Badge>
        </Popover>
    );
};
