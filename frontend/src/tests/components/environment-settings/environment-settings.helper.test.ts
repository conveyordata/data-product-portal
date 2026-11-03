import { describe, expect, it } from 'vitest';
import { buildDefaultValues, followDefaults } from '@/components/environment-settings/environment-settings.helper';
import { type EnvironmentUiMetadata, UIElementType } from '@/store/api/services/generated/pluginsApi';

const metadata = (initialValue: string): EnvironmentUiMetadata[] => [
    {
        environment_id: 'dev',
        ui_metadata: [
            {
                name: 'instance_name',
                label: 'Instance name',
                type: UIElementType.String,
                required: true,
                string: { initial_value: initialValue },
            },
        ],
    },
];

describe('buildDefaultValues', () => {
    it('fills placeholders from the shared values', () => {
        expect(buildDefaultValues(metadata('{database}-dev'), { database: 'db1' })).toEqual({
            dev: { instance_name: 'db1-dev' },
        });
    });

    it('cuts a placeholder to the length after the dot', () => {
        expect(buildDefaultValues(metadata('{database:.3}-dev'), { database: 'orders' })).toEqual({
            dev: { instance_name: 'ord-dev' },
        });
    });

    it('renders a missing shared value as empty', () => {
        expect(buildDefaultValues(metadata('{database}-dev'))).toEqual({ dev: { instance_name: '-dev' } });
    });
});

describe('followDefaults', () => {
    const defaults = (database: string) => buildDefaultValues(metadata('{database}-dev'), { database });

    it('fills live while the cell still holds the previous default', () => {
        expect(followDefaults(defaults('d'), defaults('db'), defaults('d'))).toEqual(defaults('db'));
    });

    it('stops following after a manual edit', () => {
        const edited = { dev: { instance_name: 'mine' } };

        expect(followDefaults(defaults('d'), defaults('db'), edited)).toEqual(edited);
    });
});
