import { EditOutlined, LeftOutlined, RightOutlined } from '@ant-design/icons';
import { Col, Flex, Row, Typography, theme } from 'antd';
import { type ReactNode, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';

type Props = {
    icon: ReactNode;
    title: string;
    titleExtra?: ReactNode;
    edit?: { path: string; tooltip: string };
    sidebar?: ReactNode;
    children: ReactNode;
};

export function DetailPageLayout({ icon, title, titleExtra, edit, sidebar, children }: Props) {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
    const { token } = theme.useToken();

    return (
        <Row wrap={false} gutter={token.paddingLG}>
            <Col flex="auto">
                <Flex vertical gap="middle">
                    <Flex justify="space-between" align="flex-start" gap="middle">
                        <Flex gap="middle" align="center">
                            {icon}
                            <Typography.Title level={3} ellipsis={{ tooltip: title, rows: 2 }} style={{ margin: 0 }}>
                                {title}
                            </Typography.Title>
                            {titleExtra}
                        </Flex>
                        <Flex gap="small">
                            {edit && (
                                <CircleIconButton
                                    icon={<EditOutlined />}
                                    tooltip={edit.tooltip}
                                    onClick={() => navigate(edit.path)}
                                />
                            )}
                            {sidebar && (
                                <CircleIconButton
                                    icon={sidebarCollapsed ? <LeftOutlined /> : <RightOutlined />}
                                    tooltip={sidebarCollapsed ? t('Show sidebar') : t('Hide sidebar')}
                                    onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
                                />
                            )}
                        </Flex>
                    </Flex>
                    {children}
                </Flex>
            </Col>
            {sidebar && !sidebarCollapsed && (
                <Col flex="280px">
                    <Flex vertical gap="large" align="flex-start">
                        {sidebar}
                    </Flex>
                </Col>
            )}
        </Row>
    );
}
