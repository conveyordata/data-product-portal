import { Card, Carousel, ConfigProvider, Space, Typography, theme } from 'antd';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

const { Text } = Typography;

type Props = {
    suggestions: string[];
};

export function SearchSuggestions({ suggestions }: Props) {
    const { t } = useTranslation();
    const { token } = theme.useToken();

    //Start on a random suggestion so people won't get bored by seeing the same suggestion over and over
    const initialSuggestion: number = useMemo(() => {
        return Math.floor(Math.random() * suggestions.length);
    }, [suggestions]);

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
                    <Carousel autoplay dots={false} dotPlacement={'start'} initialSlide={initialSuggestion}>
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
