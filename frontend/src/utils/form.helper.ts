export const selectFilterOptionByLabelAndValue = (input: string, option?: { label: string; value: string }) => {
    if (!option) {
        return false;
    }

    return (
        option.label.toLowerCase().includes(input.toLowerCase()) ||
        option.value.toLowerCase().includes(input.toLowerCase())
    );
};
