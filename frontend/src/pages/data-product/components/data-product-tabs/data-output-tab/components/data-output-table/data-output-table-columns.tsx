import { Badge, Button, Popconfirm, TableColumnsType } from 'antd';
//import { getDataProductDataOutputLinkBadgeStatus, getDataProductDataOutputLinkStatusLabel } from '@/utils/status.helper.ts';
import styles from './data-output-table.module.scss';
import { TFunction } from 'i18next';
import { TableCellAvatar } from '@/components/list/table-cell-avatar/table-cell-avatar.component.tsx';
//import data-outputBorderIcon from '@/assets/icons/data-output-border-icon.svg?react';
import dataOutputOutlineIcon from '@/assets/icons/data-output-outline-icon.svg?react';
import { CustomSvgIconLoader } from '@/components/icons/custom-svg-icon-loader/custom-svg-icon-loader.component.tsx';
//import { createDataOutputIdPath } from '@/types/navigation.ts';
import { DataOutput } from '@/types/data-output';
//import { RestrictedDataOutputPopoverTitle } from '@/components/data-outputs/restricted-data-output-popover-title/restricted-data-output-popover-title.tsx';
//import { RestrictedDataOutputTitle } from '@/components/data-outputs/restricted-data-output-title/restricted-data-output-title.tsx';

type Props = {
    t: TFunction;
    onRemoveDataProductDataOutputLink: (dataOutputId: string, name: string) => void;
    onCancelDataProductDataOutputLinkRequest: (dataOutputId: string, name: string) => void;
    isLoading?: boolean;
    isDisabled?: boolean;
};

export const getDataProductDataOutputsColumns = ({
    onRemoveDataProductDataOutputLink,
    onCancelDataProductDataOutputLinkRequest,
    t,
    isDisabled,
    isLoading,
}: Props): TableColumnsType<DataOutput> => {
    return [
        {
            title: t('Id'),
            dataIndex: 'id',
            hidden: true,
        },
        {
            title: t('Name'),
            dataIndex: 'name',
            render: (_, { name, external_id,configuration }) => {
                // Render different types of configuration?
                // const isRestrictedDataOutput = .access_type === 'restricted';
                // const isDataOutputRequestApproved = status === 'approved';
                // const popoverTitle = isRestrictedDataOutput ? (
                //     <RestrictedDataOutputPopoverTitle name={data-output.name} isApproved={isDataOutputRequestApproved} />
                // ) : (
                //     data-output.name
                // );
                //const title = isRestrictedDataOutput ? <RestrictedDataOutputTitle name={data-output.name} /> : data-output.name;
                return (
                    <TableCellAvatar
                        popover={{ title: name, content: external_id }}
                        //linkTo={createDataOutputIdPath(external_id)}
                        icon={<CustomSvgIconLoader iconComponent={dataOutputOutlineIcon} />}
                        title={name}
                        subtitle={
                            <Badge
                                //status={getDataProductDataOutputLinkBadgeStatus(status)}
                                //text={getDataProductDataOutputLinkStatusLabel(status)}
                                className={styles.noSelect}
                            />
                        }
                    />
                );
            },
            width: '100%',
        },
        // {
        //     title: t('Actions'),
        //     key: 'action',
        //     render: (_, { data-output, data-output_id, status }) => {
        //         const buttonText = status === 'pending_approval' ? t('Cancel') : t('Remove');
        //         const popupTitle = status === 'pending_approval' ? t('Cancel Request') : t('Remove DataOutput');
        //         const popupDescription =
        //             status === 'pending_approval'
        //                 ? t('Are you sure you want to cancel the request to link {{name}} to the data product?', {
        //                       name: data-output.name,
        //                   })
        //                 : t('Are you sure you want to remove {{name}} from the data product?', {
        //                       name: data-output.name,
        //                   });
        //         const onConfirm =
        //             status === 'pending_approval'
        //                 ? onCancelDataProductDataOutputLinkRequest
        //                 : onRemoveDataProductDataOutputLink;
        //         return (
        //             <Popconfirm
        //                 title={popupTitle}
        //                 description={popupDescription}
        //                 onConfirm={() => onConfirm(data-output_id, data-output.name)}
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
        //     },
        // },
    ];
};
