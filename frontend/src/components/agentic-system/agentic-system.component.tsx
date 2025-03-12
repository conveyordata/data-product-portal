import { Button, Flex, Form, Input, Typography } from 'antd';
import { useMemo, useState } from 'react';

import {
    useAskQuestionMutation,
    useMainAIEndpointQuery,
} from '@/store/features/agentic-system/agentic-system-api-slice';
import { useTranslation } from 'react-i18next';

export function AgenticSystem() {
    // const { data: agenticSystem } = useMainAIEndpointQuery();
    const [askQuestion, isFetching] = useAskQuestionMutation();
    const [form] = Form.useForm();
    const { t } = useTranslation();
    const [result, setResult] = useState('');
    // let result = useMemo(() => {
    //     console.log(agenticSystem);
    //     return agenticSystem?.message;
    // }, [agenticSystem]);

    const onSubmit = async (values: any) => {
        console.log(values);
        await askQuestion(values.question)
            .unwrap()
            .then((payload) => {
                setResult(payload.message);
                console.log(result);
            });
    };

    return (
        <Flex>
            <Form
                form={form}
                layout="vertical"
                onFinish={onSubmit}
                // onFinishFailed={onSubmitFailed}
                autoComplete={'off'}
                requiredMark={'optional'}
                labelWrap
            >
                <Form.Item name={'question'} label={t('Question')} tooltip={t('The question for the AI system')}>
                    <Input />
                </Form.Item>
                <Typography.Title>{result}</Typography.Title>
                <Button
                    type="primary"
                    htmlType={'submit'}
                    // loading={isCreating || isUpdating}
                    // disabled={isLoading || !canFillInForm}
                >
                    {t('Ask question')}
                </Button>
            </Form>
        </Flex>
    );
}
