import { ExperimentOutlined } from '@ant-design/icons';
import type { TFunction } from 'i18next';
import { useDispatch, useSelector } from 'react-redux';
import { selectWizardEnabled, toggleWizard } from '@/store/features/wizard/wizard-slice.ts';

export default function ToggleWizard(t: TFunction) {
    const dispatch = useDispatch();
    const wizardEnabled = useSelector(selectWizardEnabled);

    const handleToggle = () => {
        dispatch(toggleWizard());
    };

    return {
        key: 'ToggleWizard',
        icon: <ExperimentOutlined />,
        label: wizardEnabled ? t('Disable wizard') : t('Enable wizard'),
        onClick: handleToggle,
    };
}
