import { Button, Flex, Table, Typography } from 'antd';
import { useCallback, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { TableCellItem } from '@/components/list/table-cell-item/table-cell-item.component.tsx';
import AccessModesModal from '@/pages/settings/components/settings-tabs/access-policy-tab/access-modes-modal.tsx';
import { type AccessMode, useGetAccessModesQuery } from '@/store/api/services/generated/configurationAccessModesApi.ts';

export default function AccessModes() {
    const { t } = useTranslation();
    const { data: { access_modes = [] } = {}, isFetching } = useGetAccessModesQuery();

    const [openModal, setOpenModal] = useState<boolean>(false);
    const [editAccessMode, setEditAccessMode] = useState<AccessMode | undefined>(undefined);

    const handleEdit = useCallback((accessMode: AccessMode) => {
        setEditAccessMode(accessMode);
        setOpenModal(true);
    }, []);
    const cancelModal = useCallback(() => {
        setOpenModal(false);
        setEditAccessMode(undefined);
    }, []);

    return (
        <>
            <Flex vertical gap="small">
                <Flex justify="space-between" align="center">
                    <Typography.Title level={3}>{t('Access Modes')}</Typography.Title>
                    <Button type="primary" onClick={() => setOpenModal(true)}>
                        {t('Add access mode')}
                    </Button>
                </Flex>
                <Typography.Text type="secondary">
                    {t('Configure available access modes for Technical Assets and Output Ports')}
                </Typography.Text>
            </Flex>
            <Table<AccessMode>
                dataSource={access_modes}
                columns={[
                    {
                        title: t('Id'),
                        dataIndex: 'id',
                        hidden: true,
                    },
                    {
                        title: t('Name'),
                        dataIndex: 'name',
                        render: (name: string) => <TableCellItem text={name} tooltip={{ content: name }} />,
                    },
                    {
                        title: t('Description'),
                        dataIndex: 'description',
                        render: (description: string) => (
                            <TableCellItem text={description} tooltip={{ content: description }} />
                        ),
                    },
                    {
                        title: t('Actions'),
                        key: 'action',
                        width: '10%',
                        render: (record: AccessMode) => {
                            return (
                                <Button
                                    type="link"
                                    onClick={() => {
                                        handleEdit(record);
                                    }}
                                >
                                    {t('Edit')}
                                </Button>
                            );
                        },
                    },
                ]}
                rowKey={(record) => record.id}
                loading={isFetching}
                size="small"
            />
            {openModal && <AccessModesModal onClose={cancelModal} editAccessMode={editAccessMode} />}
        </>
    );
}
