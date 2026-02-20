import Icon, {
    BarChartOutlined,
    CompassOutlined,
    HistoryOutlined,
    InfoCircleOutlined,
    SettingOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import { usePostHog } from '@posthog/react';
import type { TourProps } from 'antd';
import { Badge, Flex, Tabs, Tour, Typography } from 'antd';
import { type ReactNode, type RefObject, useEffect, useMemo, useRef, useState } from 'react';
import { Trans, useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { Explorer } from '@/components/explorer/explorer';
import { HistoryTab } from '@/components/history/history-tab';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import { UsageTab } from '@/components/tabs/usage-tab/usage-tab.tsx';
import { PosthogEvents } from '@/constants/posthog.constants';
import { useTabParam } from '@/hooks/use-tab-param.tsx';
import { AboutTab } from '@/pages/data-product/components/data-product-tabs/about-tab/about-tab.tsx';
import { DataOutputTab } from '@/pages/data-product/components/data-product-tabs/data-output-tab/data-output-tab.tsx';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import { InputPortTab } from '@/pages/data-product/components/data-product-tabs/input-port-tab/input-port-tab.tsx';
import { TeamTab } from '@/pages/data-product/components/data-product-tabs/team-tab/team-tab.tsx';
import { selectCurrentUser } from '@/store/api/services/auth-slice.ts';
import { useCheckAccessQuery } from '@/store/api/services/generated/authorizationApi.ts';
import { useGetDataProductEventHistoryQuery } from '@/store/api/services/generated/dataProductsApi.ts';
import { useMarkTourAsSeenMutation } from '@/store/api/services/generated/usersApi.ts';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import styles from './data-product-tabs.module.scss';
import { SettingsTab } from './settings-tab/settings-tab';

const { Paragraph, Link } = Typography;

type Props = {
    dataProductId: string;
    isLoading: boolean;
};

type Tab = {
    label: ReactNode;
    key: TabKeys;
    ref?: RefObject<null>;
    icon?: ReactNode;
    children: ReactNode;
};

export function DataProductTabs({ dataProductId, isLoading }: Props) {
    const { t } = useTranslation();
    const posthog = usePostHog();
    const currentUser = useSelector(selectCurrentUser);
    const aboutRef = useRef(null);
    const inputPortRef = useRef(null);
    const outputPortRef = useRef(null);
    const teamRef = useRef(null);
    const { data: access } = useCheckAccessQuery({
        action: AuthorizationAction.DATA_PRODUCT__UPDATE_PROPERTIES,
        resource: dataProductId,
    });
    const [open, setOpen] = useState<boolean>(false);
    const openTour = !currentUser?.has_seen_tour && (access?.allowed ?? false);

    useEffect(() => {
        if (openTour) {
            posthog.capture(PosthogEvents.DATA_PRODUCT_TOUR_STARTED, {
                data_product_id: dataProductId,
            });
        }
        setOpen(openTour);
    }, [openTour, dataProductId, posthog]);

    const [setSeenTour] = useMarkTourAsSeenMutation();
    const { data: { events: dataProductHistoryData = [] } = {}, isLoading: isFetchingDataProductHistory } =
        useGetDataProductEventHistoryQuery(dataProductId, { skip: !dataProductId });

    const { activeTab, onTabChange } = useTabParam(TabKeys.About, Object.values(TabKeys));

    useEffect(() => {
        posthog.capture(PosthogEvents.DATA_PRODUCTS_TAB_CLICKED, {
            tab_name: activeTab,
        });
    }, [activeTab, posthog]);

    const tabs: Tab[] = useMemo(() => {
        return [
            {
                label: <Typography.Text ref={aboutRef}>{t('About')}</Typography.Text>,
                key: TabKeys.About,
                icon: <InfoCircleOutlined />,
                children: <AboutTab dataProductId={dataProductId} />,
            },
            {
                label: (
                    <Flex className={styles.betaContainer}>
                        {t('Usage')}
                        <Badge className={styles.beta} count={t('BETA')} />
                    </Flex>
                ),
                key: TabKeys.Usage,
                icon: <BarChartOutlined />,
                children: <UsageTab dataProductId={dataProductId} />,
            },
            {
                label: <Typography.Text ref={inputPortRef}>{t('Input Ports')}</Typography.Text>,
                key: TabKeys.InputPorts,
                icon: <Icon component={datasetOutlineIcon} />,
                children: <InputPortTab dataProductId={dataProductId} />,
            },
            {
                label: <Typography.Text ref={outputPortRef}>{t('Output Ports')}</Typography.Text>,
                key: TabKeys.OutputPorts,
                icon: <Icon component={dataOutputOutlineIcon} />,
                children: <DataOutputTab dataProductId={dataProductId} />,
            },
            {
                label: t('Explorer'),
                key: TabKeys.Explorer,
                icon: <CompassOutlined />,
                children: <Explorer id={dataProductId} type={'dataproduct'} />,
            },
            {
                label: <Typography.Text ref={teamRef}>{t('Team')}</Typography.Text>,
                key: TabKeys.Team,
                icon: <TeamOutlined />,
                children: <TeamTab dataProductId={dataProductId} />,
            },
            {
                label: t('Settings'),
                key: TabKeys.Settings,
                icon: <SettingOutlined />,
                children: <SettingsTab dataProductId={dataProductId} />,
            },
            {
                label: t('History'),
                key: TabKeys.History,
                icon: <HistoryOutlined />,
                children: (
                    <HistoryTab
                        id={dataProductId}
                        type={EventReferenceEntity.DataProduct}
                        history={dataProductHistoryData}
                        isFetching={isFetchingDataProductHistory}
                    />
                ),
            },
        ];
    }, [dataProductId, t, dataProductHistoryData, isFetchingDataProductHistory]);

    const steps: TourProps['steps'] = useMemo(() => {
        return [
            {
                title: t('Your first Data Product!'),
                description: t(
                    'Congratulations on creating your first Data Product! This tour will introduce you to the key features that will help you manage and improve your Data Product effectively.',
                ),
            },
            {
                title: t('Provide About'),
                description: t(
                    'The About page of your Data Product functions as a wiki page. Any relevant information about the Data Product can be documented here for easy reference by team members and stakeholders.',
                ),
                target: () => aboutRef.current,
            },
            {
                title: t('Register an Input Port'),
                description: t(
                    'This tab lists the Input Ports for your Data Product. You can request access to additional Input Ports here.',
                ),
                target: () => inputPortRef.current,
            },
            {
                title: t('Register an Output Port'),
                description: t(
                    'Define the Output Ports for your Data Product and populate them with Technical Assets by dragging and dropping. Output Ports will automatically show up in the marketplace.',
                ),
                target: () => outputPortRef.current,
            },
            {
                title: t('Set up your team'),
                description: t(
                    'Assign roles and permissions to team members to manage access and collaboration effectively.',
                ),
                target: () => teamRef.current,
            },
            {
                title: `🎉 ${t('You have finished the tour!')} 🎉`,
                description: (
                    <Typography>
                        <Typography.Paragraph>
                            {t('You are all set to start managing your Data Product!')}
                        </Typography.Paragraph>
                        <Paragraph>
                            {t('We have shown you the main features, but feel free to explore further on your own.')}
                        </Paragraph>
                        <Paragraph>
                            {t('With what you have learned you can:')}
                            <ul>
                                <li>{t('Write a comprehensive about page.')}</li>
                                <li>{t('Register Input Ports to bring data into your Data Product.')}</li>
                                <li>{t('Define Output Ports to expose data from your Data Product.')}</li>
                                <li>{t('Set up your team to manage access and collaboration.')}</li>
                            </ul>
                        </Paragraph>
                        <Paragraph>
                            <Trans t={t}>
                                If there are some concepts you are unsure about, please refer to our{' '}
                                <Link
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    href="https://docs.dataproductportal.com"
                                >
                                    documentation
                                </Link>{' '}
                                or reach out to support.
                            </Trans>
                        </Paragraph>
                    </Typography>
                ),
            },
        ];
    }, [t]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    return (
        <>
            <Tabs
                activeKey={activeTab}
                onChange={onTabChange}
                items={tabs.map(({ key, label, icon, children }) => {
                    return {
                        label,
                        key,
                        children,
                        icon,
                        disabled: !dataProductId,
                        className: styles.tabPane,
                    };
                })}
                size={'middle'}
                rootClassName={styles.tabContainer}
            />
            <Tour
                open={open}
                steps={steps}
                onChange={(current) => {
                    switch (current) {
                        case 0:
                        case 1:
                        case 5:
                            onTabChange(TabKeys.About);
                            break;
                        case 2:
                            onTabChange(TabKeys.InputPorts);
                            break;
                        case 3:
                            onTabChange(TabKeys.OutputPorts);
                            break;
                        case 4:
                            onTabChange(TabKeys.Team);
                            break;
                        default:
                            onTabChange(TabKeys.Settings);
                    }
                }}
                onClose={async (current) => {
                    posthog.capture(PosthogEvents.DATA_PRODUCT_TOUR_CLOSED, {
                        current_step: current,
                    });
                    setOpen(false);
                    onTabChange(TabKeys.About);
                    await setSeenTour();
                }}
                onFinish={() => {
                    posthog.capture(PosthogEvents.DATA_PRODUCT_TOUR_FINISHED);
                }}
            />
        </>
    );
}
