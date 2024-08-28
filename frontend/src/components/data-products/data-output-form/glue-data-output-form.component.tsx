import { Form, FormInstance, Input, Select } from 'antd';
import { useTranslation } from 'react-i18next';
import { DataOutputConfiguration, DataOutputCreateFormSchema, GlueDataOutput } from '@/types/data-output';
// import styles from './data-output-form.module.scss';
// import { useGetDataProductByIdQuery } from '@/store/features/data-products/data-products-api-slice.ts';
// import { dispatchMessage } from '@/store/features/feedback/utils/dispatch-feedback.ts';
// import { generateExternalIdFromName } from '@/utils/external-id.helper.ts';
// import { Component, MutableRefObject, useEffect, useMemo, useState } from 'react';
// import { useNavigate } from 'react-router-dom';
// import { createDataProductIdPath } from '@/types/navigation.ts';
// import { FORM_GRID_WRAPPER_COLS } from '@/constants/form.constants.ts';
// import { useCreateDataOutputMutation } from '@/store/features/data-outputs/data-outputs-api-slice';
// import { DataPlatform, DataPlatforms } from '@/types/data-platform';
// import { getDataPlatforms } from '@/pages/data-product/components/data-product-actions/data-product-actions.component';
// import { DataOutputPlatformTile } from '@/components/data-outputs/data-output-platform-tile/data-output-platform-tile.component';
// import { CustomDropdownItemProps } from '@/types/shared';

type Props = {
    sourceAligned: boolean;
    external_id: string | undefined;
    form: FormInstance<DataOutputCreateFormSchema & DataOutputConfiguration>;
};

export function GlueDataOutputForm({ form, external_id }: Props) {
    const { t } = useTranslation();

    return (
        <div>
            <Form.Item<GlueDataOutput>
                required
                name={'glue_database'}
                label={t('Glue database')}
                tooltip={t('The name of the Glue database to link the data output to')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the name of the Glue database for this data output'),
                    },
                ]}
            >
                <Input />
            </Form.Item>
            <Form.Item<GlueDataOutput>
                required
                name={'table_prefixes'}
                label={t('Table prefixes')}
                tooltip={t('The tables that your data output can access')}
                rules={[
                    {
                        required: true,
                        message: t('Please input the tables this data output can access'),
                    },
                ]}
            >
                <Select tokenSeparators={[',']} placeholder={t('Provide table prefixes')} mode={'tags'} options={[]} />
            </Form.Item>
        </div>
    );
}
