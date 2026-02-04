import { Card, Carousel, ConfigProvider, Space, Typography, theme } from 'antd';
import { useTranslation } from 'react-i18next';

const { Text } = Typography;

type Props = {
    suggestions: string[] | undefined;
};

export function SearchSuggestions({ suggestions }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();

    if (!suggestions) {
        return null;
    }

    return (
        <ConfigProvider
            theme={{
                components: {
                    Card: {
                        colorBgContainer: token.colorFillAlter,
                        boxShadowTertiary: 'none',
                    },
                },
            }}
        >
            <Card size="small" variant={'borderless'}>
                <Space>
                    <Text type="secondary" style={{ whiteSpace: 'nowrap' }}>
                        {t('Try searching for:')}
                    </Text>
                    <Carousel autoplay dots={false} dotPlacement={'start'}>
                        {suggestions.map((item) => (
                            <Text strong key={item}>
                                {item}
                            </Text>
                        ))}
                    </Carousel>
                </Space>
            </Card>
        </ConfigProvider>
    );
}
