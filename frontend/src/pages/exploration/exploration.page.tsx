import { EditOutlined, ProductOutlined, RocketOutlined } from '@ant-design/icons';
import { Flex, Space, Tabs, Typography } from 'antd';
import { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useNavigate, useParams } from 'react-router';
import explorationBorderIcon from '@/assets/icons/border-icons/exploration-border-icon.svg?react';
import { CircleIconButton } from '@/components/buttons/circle-icon-button/circle-icon-button.tsx';
import { OutputPortOutlined } from '@/components/icons';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { useBreadcrumbs } from '@/components/layout/navbar/breadcrumbs/breadcrumb.context.tsx';
import { useTabParam } from '@/hooks/use-tab-param.tsx';
import { ExplorationInputPorts } from '@/pages/exploration/components/exploration-input-ports.tsx';
import { ExplorationStart } from '@/pages/exploration/components/exploration-start.tsx';
import { ExplorationTabKeys } from '@/pages/exploration/exploration-tab-keys.ts';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useGetExplorationQuery } from '@/store/api/services/generated/explorationsApi.ts';
import { ApplicationPaths, DynamicPathParams } from '@/types/navigation.ts';
import { getDynamicRoutePath } from '@/utils/routes.helper.ts';

export function ExplorationPage() {
    const { t } = useTranslation();
    const navigate = useNavigate();
    const currentUser = useSelector(selectCurrentUser);
    const { explorationId = undefined } = useParams();
    const { activeTab, onTabChange } = useTabParam(ExplorationTabKeys.Start, Object.values(ExplorationTabKeys));

    const { data: exploration, error: fetchingExplorationError } = useGetExplorationQuery(explorationId ?? '', {
        skip: explorationId === undefined,
    });
    const { setBreadcrumbs } = useBreadcrumbs();
    useEffect(() => {
        setBreadcrumbs([
            {
                title: (
                    <>
                        <ProductOutlined />
                        {t('Product Studio')}
                    </>
                ),
                path: ApplicationPaths.Studio,
            },
            { title: exploration?.name },
        ]);
    }, [setBreadcrumbs, exploration, t]);
    if (explorationId === undefined || explorationId === null) {
        navigate(ApplicationPaths.Studio, { replace: true });
        return null;
    }
    if (fetchingExplorationError) {
        navigate(ApplicationPaths.Studio, { replace: true });
        return null;
    }

    const canEdit = exploration?.owner.id === currentUser?.id;

    const navigateToEditPage = () => {
        const destination = getDynamicRoutePath(
            ApplicationPaths.ExplorationEdit,
            DynamicPathParams.ExplorationId,
            explorationId,
        );
        return navigate(destination);
    };

    return (
        <Flex vertical gap="middle">
            <Flex gap="middle" align="center" justify="space-between">
                <Flex gap="middle" align="center" justify="center">
                    <CustomSvgIconLoader iconComponent={explorationBorderIcon} size="large" />
                    <Typography.Title
                        level={3}
                        style={{ margin: 0 }}
                        ellipsis={{ tooltip: exploration?.name, rows: 2 }}
                    >
                        {exploration?.name}
                    </Typography.Title>
                </Flex>

                {canEdit && (
                    <CircleIconButton
                        icon={<EditOutlined />}
                        tooltip={t('Edit Data Product')}
                        onClick={navigateToEditPage}
                    />
                )}
            </Flex>
            <Space size="large">
                <Flex gap="small">
                    <Typography.Text strong>{t('Domain')}</Typography.Text>
                    <Typography.Text>{exploration?.domain.name}</Typography.Text>
                </Flex>
                <Flex gap="small">
                    <Typography.Text strong>{t('Owner')}</Typography.Text>
                    <Typography.Text>{`${exploration?.owner?.first_name} ${exploration?.owner?.last_name} <${exploration?.owner?.email}>`}</Typography.Text>
                </Flex>
                <Flex gap="small">
                    <Typography.Text strong>{t('Namespace')}</Typography.Text>
                    <Typography.Text>{exploration?.namespace}</Typography.Text>
                </Flex>
            </Space>
            <Typography.Paragraph italic>{exploration?.description}</Typography.Paragraph>
            <Tabs
                activeKey={activeTab}
                onChange={onTabChange}
                items={[
                    {
                        label: t('Start Exploring'),
                        icon: <RocketOutlined />,
                        key: ExplorationTabKeys.Start,
                        children: <ExplorationStart />,
                    },
                    {
                        label: <Typography.Text>{t('Input Ports')}</Typography.Text>,
                        key: ExplorationTabKeys.InputPorts,
                        icon: <OutputPortOutlined />,
                        children: <ExplorationInputPorts explorationId={explorationId} />,
                    },
                ]}
            />
        </Flex>
    );
}
