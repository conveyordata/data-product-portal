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

export function DataProductTabs({ dataProductId, isLoading }: Props) {
    const { t } = useTranslation();
    const currentUser = useSelector(selectCurrentUser);
    const ref1 = useRef(null);
    const ref2 = useRef(null);
    const ref3 = useRef(null);
    const ref4 = useRef(null);
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
    }, [openTour]);
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
                label: <Typography.Text ref={ref1}>{t('About')}</Typography.Text>,
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
                label: <Typography.Text ref={ref2}>{t('Input Ports')}</Typography.Text>,
                key: TabKeys.Datasets,
                icon: <Icon component={datasetOutlineIcon} />,
                children: <DatasetTab dataProductId={dataProductId} />,
            },
            {
                label: <Typography.Text ref={ref3}>{t('Output Ports')}</Typography.Text>,
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
                label: <Typography.Text ref={ref4}>{t('Team')}</Typography.Text>,
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

    const steps: TourProps['steps'] = [
        {
            title: 'Provide About',
            description:
                'The About page of your data product functions as a wiki page. Any relevant information about the data product can be documented here for easy reference by team members and stakeholders.',
            cover: (
                <img
                    draggable={false}
                    alt="tour.png"
                    src="https://user-images.githubusercontent.com/5378891/197385811-55df8480-7ff4-44bd-9d43-a7dade598d70.png"
                />
            ),
            target: () => ref1.current,
        },
        {
            title: 'Register an Input Port',
            description:
                'Define the input port for your data product. If you have not yet requested them at creation time you can request read access to additional input ports here.',
            target: () => ref2.current,
        },
        {
            title: 'Register an Output Port',
            description:
                'Define the output ports for your data product and populate them with technical assets by dragging and dropping.',
            target: () => ref3.current,
        },
        {
            title: 'Set up your team',
            description: 'Assign roles and permissions to team members to manage access and collaboration effectively.',
            target: () => ref4.current,
        },
    ];

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
                        current === 0
                            ? TabKeys.About
                            : current === 1
                              ? TabKeys.Datasets
                              : current === 2
                                ? TabKeys.DataOutputs
                                : current === 3
                                  ? TabKeys.Team
                                  : TabKeys.Settings,
                    )
                }
                onClose={(current) => {
                    setOpen(false);
                    setActiveTab(TabKeys.About);
                    posthog.capture(PosthogEvents.DATA_PRODUCT_TOUR_CLOSED, {
                        current_step: current,
                    });
                    setSeenTour();
                }}
                onFinish={() => {
                    posthog.capture(PosthogEvents.DATA_PRODUCT_TOUR_FINISHED);
                }}
                steps={steps}
            />
        </>
    );
}
