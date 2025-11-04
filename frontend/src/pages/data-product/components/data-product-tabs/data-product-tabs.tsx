import Icon, {
    BarChartOutlined,
    CompassOutlined,
    HistoryOutlined,
    InfoCircleOutlined,
    SettingOutlined,
    TeamOutlined,
} from '@ant-design/icons';
import type { TourProps } from 'antd';
import { Badge, Flex, Tabs, Tour, Typography } from 'antd';
import { type ReactElement, type ReactNode, useEffect, useMemo, useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useSelector } from 'react-redux';
import { useLocation, useNavigate } from 'react-router';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import datasetOutlineIcon from '@/assets/icons/dataset-outline-icon.svg?react';
import { Explorer } from '@/components/explorer/explorer';
import { HistoryTab } from '@/components/history/history-tab';
import { LoadingSpinner } from '@/components/loading/loading-spinner/loading-spinner.tsx';
import posthog from '@/config/posthog-config';
import { PosthogEvents } from '@/constants/posthog.constants';
import { AboutTab } from '@/pages/data-product/components/data-product-tabs/about-tab/about-tab.tsx';
import { DataOutputTab } from '@/pages/data-product/components/data-product-tabs/data-output-tab/data-output-tab.tsx';
import { TabKeys } from '@/pages/data-product/components/data-product-tabs/data-product-tabkeys.ts';
import { DatasetTab } from '@/pages/data-product/components/data-product-tabs/dataset-tab/dataset-tab.tsx';
import { TeamTab } from '@/pages/data-product/components/data-product-tabs/team-tab/team-tab.tsx';
import { selectCurrentUser } from '@/store/features/auth/auth-slice';
import { useCheckAccessQuery } from '@/store/features/authorization/authorization-api-slice';
import { useGetDataProductHistoryQuery } from '@/store/features/data-products/data-products-api-slice';
import { useSeenTourMutation } from '@/store/features/users/users-api-slice';
import { AuthorizationAction } from '@/types/authorization/rbac-actions';
import { EventReferenceEntity } from '@/types/events/event-reference-entity';
import { UsageTab } from '../../../../components/tabs/usage-tab/usage-tab';
import styles from './data-product-tabs.module.scss';
import { SettingsTab } from './settings-tab/settings-tab';

type Props = {
    dataProductId: string;
    isLoading: boolean;
};

type Tab = {
    label: string | ReactElement;
    key: TabKeys;
    ref?: React.RefObject<null>;
    icon?: ReactNode;
    children: ReactNode;
};
const { Paragraph, Link } = Typography;

export function DataProductTabs({ dataProductId, isLoading }: Props) {
    const { t } = useTranslation();
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
    const openTour = !currentUser?.has_seen_tour && access?.allowed;

    useEffect(() => {
        if (openTour) {
            posthog.capture(PosthogEvents.DATA_PRODUCT_TOUR_STARTED, {
                data_product_id: dataProductId,
            });
        }
        setOpen(openTour || false);
    }, [openTour, dataProductId]);
    const [setSeenTour] = useSeenTourMutation();
    const location = useLocation();
    const navigate = useNavigate();
    const { data: dataProductHistoryData, isLoading: isFetchingDataProductHistory } = useGetDataProductHistoryQuery(
        dataProductId,
        { skip: !dataProductId },
    );
    const [activeTab, setActiveTab] = useState(location.hash.slice(1) || TabKeys.About);

    useEffect(() => {
        posthog.capture(PosthogEvents.DATA_PRODUCTS_TAB_CLICKED, {
            tab_name: activeTab,
        });
    }, [activeTab]);

    useEffect(() => {
        const hash = location.hash.slice(1);
        if (hash) {
            setActiveTab(hash);
        }
    }, [location]);

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
                key: TabKeys.Datasets,
                icon: <Icon component={datasetOutlineIcon} />,
                children: <DatasetTab dataProductId={dataProductId} />,
            },
            {
                label: <Typography.Text ref={outputPortRef}>{t('Output Ports')}</Typography.Text>,
                key: TabKeys.DataOutputs,
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
                title: t('Your first data product!'),
                description: t(
                    'Congratulations on creating your first data product! This tour will introduce you to the key features that will help you manage and improve your data product effectively.',
                ),
            },
            {
                title: t('Provide About'),
                description: t(
                    'The About page of your data product functions as a wiki page. Any relevant information about the data product can be documented here for easy reference by team members and stakeholders.',
                ),
                target: () => aboutRef.current,
            },
            {
                title: t('Register an Input Port'),
                description: t(
                    'This tab lists the input ports for your data product. You can request access to additional input ports here.',
                ),
                target: () => inputPortRef.current,
            },
            {
                title: t('Register an Output Port'),
                description: t(
                    'Define the output ports for your data product and populate them with technical assets by dragging and dropping. Output ports will automatically show up in the marketplace.',
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
                title: t('🎉 You have finished the tour! 🎉'),
                description: (
                    <Typography>
                        <Typography.Paragraph>
                            {t('You are all set to start managing your data product!')}
                        </Typography.Paragraph>
                        <Paragraph>
                            {t('We have shown you the main features, but feel free to explore further on your own.')}
                        </Paragraph>
                        <Paragraph>
                            {t('With what you have learned you can:')}
                            <ul>
                                <li>{t('Write a comprehensive about page.')}</li>
                                <li>{t('Register input ports to bring data into your data product.')}</li>
                                <li>{t('Define output ports to expose data from your data product.')}</li>
                                <li>{t('Set up your team to manage access and collaboration.')}</li>
                            </ul>
                        </Paragraph>
                        <Paragraph>
                            {t('If there are some concepts you are unsure about, please refer to our ')}{' '}
                            <Link target="_blank" rel="noopener noreferrer" href="https://docs.dataproductportal.com">
                                {t('documentation')}
                            </Link>{' '}
                            {t(' or reach out to support.')}
                        </Paragraph>
                    </Typography>
                ),
            },
        ];
    }, [t]);

    if (isLoading) {
        return <LoadingSpinner />;
    }

    const onTabChange = (key: string) => {
        navigate(`#${key}`);
    };

    return (
        <>
            <Tabs
                activeKey={activeTab}
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
                onChange={onTabChange}
            />
            <Tour
                open={open}
                onChange={(current) =>
                    setActiveTab(
                        current === 0 || current === 1 || current === 5
                            ? TabKeys.About
                            : current === 2
                              ? TabKeys.Datasets
                              : current === 3
                                ? TabKeys.DataOutputs
                                : current === 4
                                  ? TabKeys.Team
                                  : TabKeys.Settings,
                    )
                }
                onClose={async (current) => {
                    setOpen(false);
                    setActiveTab(TabKeys.About);
                    posthog.capture(PosthogEvents.DATA_PRODUCT_TOUR_CLOSED, {
                        current_step: current,
                    });
                    await setSeenTour();
                }}
                onFinish={() => {
                    posthog.capture(PosthogEvents.DATA_PRODUCT_TOUR_FINISHED);
                }}
                steps={steps}
            />
        </>
    );
}
