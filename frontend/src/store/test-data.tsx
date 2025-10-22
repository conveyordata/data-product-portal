const draftLifecycle = {
    id: '123',
    value: 1,
    name: 'Draft',
    color: 'grey',
    is_default: true,
};
export const cartData = [
    {
        outputPortName: 'Output port A',
        dataProductName: 'Data product A',
        description: 'Description of data product A',
        domain: 'Clinical',
        dataProductLifecycle: draftLifecycle,
    },
    {
        outputPortName: 'Output port B',
        dataProductName: 'Data product A',
        description: 'Description of data product A',
        domain: 'Clinical',
        dataProductLifecycle: draftLifecycle,
    },
    {
        outputPortName: 'Output port A',
        dataProductName: 'Data product B',
        description: 'Description of data product B',
        domain: 'Manufacturing',
        dataProductLifecycle: draftLifecycle,
    },
    {
        outputPortName: 'Output port A',
        dataProductName: 'Data product C',
        description: 'Description of data product C',
        domain: 'HR',
        dataProductLifecycle: draftLifecycle,
    },
];
