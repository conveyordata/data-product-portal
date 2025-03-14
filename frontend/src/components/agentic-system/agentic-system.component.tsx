import { Button, Flex, Form, Input } from 'antd';
import { useState } from 'react';
import { useTranslation } from 'react-i18next';
import MarkDown from 'react-markdown';
import rehypeRaw from 'rehype-raw';
import rehypeSanitize from 'rehype-sanitize';
import remarkBreaks from 'remark-breaks';
import remarkGfm from 'remark-gfm';

import { useAskQuestionMutation } from '@/store/features/agentic-system/agentic-system-api-slice';

import { LoadingSpinner } from '../loading/loading-spinner/loading-spinner';

export function AgenticSystem() {
    // const { data: agenticSystem } = useMainAIEndpointQuery();
    const [askQuestion, { isLoading }] = useAskQuestionMutation();
    const [form] = Form.useForm();
    const { t } = useTranslation();
    const [result, setResult] = useState('');
    // let result = useMemo(() => {
    //     console.log(agenticSystem);
    //     return agenticSystem?.message;
    // }, [agenticSystem]);
    const onSubmit = async (values: { question: string }) => {
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

                {/* <ReactMarkDown>{result}</ReactMarkDown> */}
                {/* <Typography.Title>{result}</Typography.Title> */}
                {(() => {
                    if (isLoading) {
                        return <LoadingSpinner />;
                    } else {
                        return (
                            <MarkDown
                                children={result}
                                remarkPlugins={[remarkGfm, remarkBreaks]}
                                rehypePlugins={[rehypeRaw, rehypeSanitize]}
                            ></MarkDown>
                        );
                    }
                })()}
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
