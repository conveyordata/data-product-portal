import { Badge, Button, List, Popconfirm, TableColumnsType, Typography } from 'antd';
//import { getDataProductDataOutputLinkBadgeStatus, getDataProductDataOutputLinkStatusLabel } from '@/utils/status.helper.ts';
import styles from './data-output-table.module.scss';
import { TFunction } from 'i18next';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
//import data-outputBorderIcon from '@/assets/icons/data-output-border-icon.svg?react';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
import { LinkOutlined } from '@ant-design/icons';
//import { createDataOutputIdPath } from '@/types/navigation.ts';
import { DataOutput } from '@/types/data-output';
import datasetBorderIcon from '@/assets/icons/dataset-border-icon.svg?react';
import { DataOutputsGetContract } from '@/types/data-output/data-output-get.contract';
import { getDataOutputIcon } from '@/utils/data-output-type-icon.helper';
import { DataOutputSubtitle } from '@/components/data-outputs/data-output-subtitle/data-output-subtitle.component';
import { DataOutputDatasetLink } from '@/types/data-output/dataset-link.contract';
import { AddDatasetPopup } from '../../../dataset-tab/components/add-dataset-popup/add-dataset-popup';
import Popover from 'antd/lib/popover';
import { useModal } from '@/hooks/use-modal';
import { SetStateAction } from 'react';
import { AddDataOutputPopup } from '../add-data-output-popup/add-data-output-popup';
import { RestrictedDatasetPopoverTitle } from '@/components/datasets/restricted-dataset-popover-title/restricted-dataset-popover-title';
import { RestrictedDatasetTitle } from '@/components/datasets/restricted-dataset-title/restricted-dataset-title';
import { createDatasetIdPath } from '@/types/navigation';
import { getDataOutputDatasetLinkBadgeStatus, getDataOutputDatasetLinkStatusLabel } from '@/utils/status.helper';
//import { RestrictedDataOutputPopoverTitle } from '@/components/data-outputs/restricted-data-output-popover-title/restricted-data-output-popover-title.tsx';
//import { RestrictedDataOutputTitle } from '@/components/data-outputs/restricted-data-output-title/restricted-data-output-title.tsx';

type Props = {
    t: TFunction;
    isLoading?: boolean;
    isDisabled?: boolean;
    handleOpen: (id: string) => void;
};

export const getDataProductDataOutputsColumns = ({
    t,
    handleOpen,
    isDisabled,
    isLoading,
}: Props): TableColumnsType<DataOutputsGetContract> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { id, name, description, configuration_type }) => {
                return (
                    <TableCellAvatar
                        popover={{ title: name, content: description }}
                        //linkTo={createDataOutputIdPath(external_id)}
                        icon={<CustomSvgIconLoader iconComponent={getDataOutputIcon(configuration_type)!}/>}
                        title={name}
                        subtitle={
                            <DataOutputSubtitle data_output_id={id}/>
                            //configuration_type
                            // <Badge
                            //     //status={getDataProductDataOutputLinkBadgeStatus(status)}
                            //     //text={configuration_type}
                            //     className={styles.noSelect}
                            // />
                        }
                    />
                );
            },
            width: '50%',
        },
        {
            title: t('Datasets'),
            dataIndex: 'links',
            render: (_, { dataset_links }) => {
                return (
                    <List
                    //loading={isLoading || isFetchingUsers}
                    size={'large'}
                    locale={{ emptyText: t('No datasets linked') }}
                    rowKey={(dataset_link: DataOutputDatasetLink) => dataset_link.dataset_id}
                    dataSource={dataset_links}
                    renderItem={(dataset_link) => {
                        const isRestrictedDataset = dataset_link.dataset.access_type === 'restricted';
                        const isDatasetRequestApproved = status === 'approved';
                        const popoverTitle = isRestrictedDataset ? (
                            <RestrictedDatasetPopoverTitle name={dataset_link.dataset.name} isApproved={isDatasetRequestApproved} />
                        ) : (
                            dataset_link.dataset.name
                        );
                        const title = isRestrictedDataset ? <RestrictedDatasetTitle name={dataset_link.dataset.name} /> : dataset_link.dataset.name;
                        return (
                            <List.Item key={dataset_link.dataset_id}>
                                <TableCellAvatar
                                    popover={{ title: popoverTitle, content: dataset_link.dataset.description }}
                                    linkTo={createDatasetIdPath(dataset_link.dataset.id)}
                                    icon={<CustomSvgIconLoader iconComponent={datasetBorderIcon} />}
                                    title={title}
                                    subtitle={
                                        <Badge
                                            status={getDataOutputDatasetLinkBadgeStatus(dataset_link.status)}
                                            text={getDataOutputDatasetLinkStatusLabel(dataset_link.status)}
                                            className={styles.noSelect}
                                        />
                                    }
                                />
                            </List.Item>
                        );
                    }}>
                    </List>
                )
            },
            width: '50%',
        },
        {
            title: t('Actions'),
            key: 'action',
            render: (_, {id, owner_id }) => {
                return <>
                <Popover content={t('Link dataset')}>
            <Button
                type="primary"
                className={styles.submitButton}
                onClick={() => {handleOpen(id);}}
                disabled={isDisabled || isLoading}// || isSubmitting}
                icon={<LinkOutlined />}
            />
            </Popover>
            </>
            }
        //     render: (_, { dataset, dataset_id, status }) => {
        //         const buttonText = status === 'pending_approval' ? t('Cancel') : t('Remove');
        //         const popupTitle = status === 'pending_approval' ? t('Cancel Request') : t('Remove Dataset');
        //         const popupDescription =
        //             status === 'pending_approval'
        //                 ? t('Are you sure you want to cancel the request to link {{name}} to the data product?', {
        //                       name: dataset.name,
        //                   })
        //                 : t('Are you sure you want to remove {{name}} from the data product?', {
        //                       name: dataset.name,
        //                   });
        //         const onConfirm =
        //             status === 'pending_approval'
        //                 ? onCancelDataProductDatasetLinkRequest
        //                 : onRemoveDataProductDatasetLink;
        //         return (
        //             <Popconfirm
        //                 title={popupTitle}
        //                 description={popupDescription}
        //                 onConfirm={() => onConfirm(dataset_id, dataset.name)}
        //                 placement={'leftTop'}
        //                 okText={t('Confirm')}
        //                 cancelText={t('Cancel')}
        //                 okButtonProps={{ loading: isLoading }}
        //                 autoAdjustOverflow={true}
        //             >
        //                 <Button loading={isLoading} disabled={isLoading || isDisabled} type={'link'}>
        //                     {buttonText}
        //                 </Button>
        //             </Popconfirm>
        //         );
        // },
        },
    ];
};
