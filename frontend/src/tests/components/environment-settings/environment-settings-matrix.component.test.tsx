import { useState } from 'react';
import { describe, expect, it, vi } from 'vitest';
import { EnvironmentChangesModal } from '@/components/environment-settings/environment-changes-modal.component.tsx';
import {
    buildDefaultValues,
    computeChanges,
    type EnvironmentSettingsError,
    type EnvironmentValues,
} from '@/components/environment-settings/environment-settings.helper.ts';
import { EnvironmentSettingsMatrix } from '@/components/environment-settings/environment-settings-matrix.component.tsx';
import {
    type EnvironmentUiMetadata,
    UIElementType,
    type UiElementMetadata,
} from '@/store/api/services/generated/pluginsApi.ts';
import { mockEnvironments } from '@/tests/mocks/configurationEnvironments.ts';
import { renderWithProviders, screen, userEvent, within } from '@/tests/test-utils.tsx';

const environments = mockEnvironments.slice(0, 2);

const sizeField = (initial: string, disabledOption: string): UiElementMetadata => ({
    name: 'size',
    label: 'Size',
    type: UIElementType.Select,
    required: true,
    select: {
        initial_value: initial,
        options: [
            { label: 'small', value: 'small', disabled: disabledOption === 'small' },
            { label: 'medium', value: 'medium', disabled: disabledOption === 'medium' },
            { label: 'large', value: 'large', disabled: disabledOption === 'large' },
        ],
    },
});

const metadata: EnvironmentUiMetadata[] = [
    { environment_id: 'env-dev', ui_metadata: [sizeField('small', 'large')] },
    { environment_id: 'env-prd', ui_metadata: [sizeField('medium', 'small')] },
];

const defaults = buildDefaultValues(metadata);

function Harness({
    initial = defaults,
    errors = [],
    withBaseline = true,
}: {
    withBaseline?: boolean;
    initial?: EnvironmentValues;
    errors?: EnvironmentSettingsError[];
}) {
    const [value, setValue] = useState(initial);
    return (
        <EnvironmentSettingsMatrix
            environments={environments}
            metadata={metadata}
            value={value}
            onChange={setValue}
            baseline={withBaseline ? defaults : undefined}
            baselineNote={(v) => `Changed from default (${v})`}
            errors={errors}
        />
    );
}

describe('EnvironmentSettingsMatrix', () => {
    it('shows the environment columns prefilled with defaults', () => {
        renderWithProviders(<Harness />);

        expect(screen.getAllByText('dev')[0]).toBeInTheDocument();
        expect(screen.getAllByText('Production')[0]).toBeInTheDocument();
        expect(screen.getByText('small')).toBeInTheDocument();
        expect(screen.getByText('medium')).toBeInTheDocument();
        expect(screen.queryByText(/Changed from default/)).not.toBeInTheDocument();
    });

    it.each([
        ['follows the given order when positions are set', ['env-prd', 'env-dev'], ['prd', 'dev']],
        ['keeps the given order when no positions are set', ['env-dev', 'env-prd'], ['dev', 'prd']],
    ])('renders columns in order: %s', (_, ids, acronyms) => {
        const ordered = ids.map((id) => mockEnvironments.find((e) => e.id === id) as (typeof environments)[number]);
        renderWithProviders(<EnvironmentSettingsMatrix environments={ordered} metadata={metadata} />);

        const headers = screen.getAllByRole('columnheader').slice(1);
        expect(headers.map((header) => header.textContent?.slice(0, 3))).toEqual(acronyms);
    });

    it('matches numeric stored values against string options', () => {
        renderWithProviders(<Harness initial={{ 'env-dev': { size: 'small' }, 'env-prd': { size: 'medium' } }} />);

        expect(screen.getByText('small')).toBeInTheDocument();
    });

    it('shows disabled options but does not allow selecting them', async () => {
        renderWithProviders(<Harness />);

        await userEvent.click(screen.getByLabelText('Size env-dev'));
        const option = (await screen.findByText('large')).closest('.ant-select-item-option');

        expect(option).toHaveClass('ant-select-item-option-disabled');
        await userEvent.click(option as HTMLElement);
        expect(screen.queryByText(/Changed from default/)).not.toBeInTheDocument();
    });

    it('explains a disabled option on hover', async () => {
        renderWithProviders(<Harness />);

        await userEvent.click(screen.getByLabelText('Size env-dev'));
        await userEvent.hover(await screen.findByText('large'));

        expect(await screen.findByText(/can't be selected in this Environment/)).toBeInTheDocument();
    });

    it('shows the tooltip of a setting', async () => {
        const withTooltip = metadata.map((item) => ({
            ...item,
            ui_metadata: item.ui_metadata.map((field) => ({ ...field, tooltip: 'How big the database is' })),
        }));
        renderWithProviders(
            <EnvironmentSettingsMatrix environments={environments} metadata={withTooltip} value={defaults} />,
        );

        await userEvent.hover(document.querySelector('.anticon-question-circle') as HTMLElement);

        expect(await screen.findByText('How big the database is')).toBeInTheDocument();
    });

    it('notes a change from the default', async () => {
        renderWithProviders(<Harness />);

        await userEvent.click(screen.getByLabelText('Size env-prd'));
        await userEvent.click(await screen.findByTitle('large'));

        expect(screen.getByText('Changed from default (medium)')).toBeInTheDocument();
    });

    it('shows no change note or highlight without a baseline', async () => {
        renderWithProviders(<Harness withBaseline={false} />);

        await userEvent.click(screen.getByLabelText('Size env-prd'));
        await userEvent.click(await screen.findByTitle('large'));

        expect(screen.queryByText(/Changed from default/)).not.toBeInTheDocument();
        expect(document.querySelector('.ant-select-status-warning')).toBeNull();
    });

    it('shows cell and environment level errors', () => {
        renderWithProviders(
            <Harness
                errors={[
                    { environment_id: 'env-prd', field: 'size', message: 'Size not allowed' },
                    { environment_id: 'env-dev', field: null, message: 'Environment is locked' },
                ]}
            />,
        );

        expect(screen.getByText('Size not allowed')).toBeInTheDocument();
        expect(screen.getAllByText('Environment is locked')[0]).toBeInTheDocument();
    });
});

describe('EnvironmentChangesModal', () => {
    it('lists changes per environment and marks unaffected ones', () => {
        const current = { ...defaults, 'env-prd': { size: 'large' } };
        const changes = computeChanges(metadata, defaults, current);
        const onConfirm = vi.fn();

        renderWithProviders(
            <EnvironmentChangesModal
                open
                environments={environments}
                changes={changes}
                onConfirm={onConfirm}
                onCancel={vi.fn()}
            />,
        );

        const prd = within(screen.getByTestId('changes-prd'));
        expect(prd.getByText('Will be updated')).toBeInTheDocument();
        expect(prd.getByText('medium')).toBeInTheDocument();
        expect(prd.getByText('large')).toBeInTheDocument();
        expect(
            within(screen.getByTestId('changes-dev')).getByText('No changes. This Environment is not reprovisioned.'),
        ).toBeInTheDocument();
    });

    it('confirms with Save Changes', async () => {
        const onConfirm = vi.fn();
        renderWithProviders(
            <EnvironmentChangesModal
                open
                environments={environments}
                changes={{}}
                onConfirm={onConfirm}
                onCancel={vi.fn()}
            />,
        );

        await userEvent.click(screen.getByRole('button', { name: 'Save Changes' }));

        expect(onConfirm).toHaveBeenCalled();
    });
});
