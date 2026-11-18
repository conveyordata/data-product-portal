import type { ReactNode } from 'react';
import { Route, Routes } from 'react-router';
import { describe, expect, it } from 'vitest';
import { DetailPageLayout } from '@/components/detail-page-layout/detail-page-layout.component.tsx';
import { renderWithProviders, screen, userEvent } from '@/tests/test-utils';

function renderLayout(props: { edit?: { path: string; tooltip: string }; sidebar?: ReactNode }) {
    return renderWithProviders(
        <Routes>
            <Route
                path="/entity"
                element={
                    <DetailPageLayout icon={null} title="Entity name" {...props}>
                        Page content
                    </DetailPageLayout>
                }
            />
            <Route path="/entity/edit" element="Edit page" />
        </Routes>,
        { routerProps: { initialEntries: ['/entity'] } },
    );
}

describe('DetailPageLayout', () => {
    it('renders the title and content', () => {
        renderLayout({});

        expect(screen.getByText('Entity name')).toBeInTheDocument();
        expect(screen.getByText('Page content')).toBeInTheDocument();
    });

    it('hides the edit button without edit', () => {
        renderLayout({});

        expect(screen.queryByLabelText('edit')).not.toBeInTheDocument();
    });

    it('navigates to the edit path', async () => {
        renderLayout({ edit: { path: '/entity/edit', tooltip: 'Edit entity' } });

        await userEvent.click(screen.getByLabelText('edit'));

        expect(await screen.findByText('Edit page')).toBeInTheDocument();
    });

    it('collapses and expands the sidebar', async () => {
        renderLayout({ sidebar: 'Sidebar content' });

        await userEvent.click(screen.getByLabelText('right'));
        expect(screen.queryByText('Sidebar content')).not.toBeInTheDocument();

        await userEvent.click(screen.getByLabelText('left'));
        expect(screen.getByText('Sidebar content')).toBeInTheDocument();
    });

    it('has no sidebar toggle without a sidebar', () => {
        renderLayout({});

        expect(screen.queryByLabelText('right')).not.toBeInTheDocument();
    });
});
