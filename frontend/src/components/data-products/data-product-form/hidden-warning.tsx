import { useTranslation } from 'react-i18next';

export const HiddenWarningText = () => {
    const { t } = useTranslation();
    return t(
        "Only use a hidden Data Product when it's really required. A hidden Data Product is hidden from the organisation, which makes it very hard to consume by others. Only use it when the knowledge of this Data Product is sensitive to the organisation.",
    );
};
