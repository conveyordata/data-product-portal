import { DeleteOutlined, ShoppingCartOutlined } from '@ant-design/icons';
import { Badge, Button, Descriptions, Flex, List, Popover, Typography } from 'antd';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import styles from '@/components/layout/navbar/cli-download/cli-download-button.module.scss';
import { useGetAllDatasetsQuery } from '@/store/features/datasets/datasets-api-slice.ts';
import { ApplicationPaths } from '@/types/navigation.ts';

const ShoppingCartItems = () => {
    const navigate = useNavigate();
    const { t } = useTranslation();
    const { data: datasets, isFetching } = useGetAllDatasetsQuery();

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
            loading={isFetching}
            dataSource={datasets}
            renderItem={(item) => (
                <List.Item>
                    <Flex justify="space-between" align="start">
                        <Descriptions
                            title={item.name}
                            column={1}
                            items={[
                                {
                                    key: 0,
                                    label: (
                                        <Typography.Text ellipsis={{}} strong>
                                            Data product
                                        </Typography.Text>
                                    ),
                                    children: item.data_product_name,
                                },
                            ]}
                        />
                        <Button type={'text'} icon={<DeleteOutlined />} danger style={{ marginLeft: 'auto' }} />
                    </Flex>
                </List.Item>
            )}
        />
    );
};

export const CartButton = () => {
    const { data: datasets } = useGetAllDatasetsQuery();
    return (
        <Popover content={<ShoppingCartItems />} trigger={'hover'} placement="bottom">
            <Badge count={datasets?.length}>
                <Button shape={'circle'} className={styles.iconButton} icon={<ShoppingCartOutlined />} />
            </Badge>
        </Popover>
    );
};
