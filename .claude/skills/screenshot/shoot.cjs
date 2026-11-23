const { chromium } = require('playwright');

const [base, out, suffix, ...pages] = process.argv.slice(2);
const widths = (process.env.SHOOT_WIDTHS || '1440').split(' ').map(Number);
const labelWidth = Boolean(process.env.SHOOT_WIDTHS);

(async () => {
    const browser = await chromium.launch({ args: ['--disable-web-security'] });
    for (const width of widths) {
        const page = await browser.newPage({ viewport: { width, height: 1300 } });
        for (const entry of pages) {
            const split = entry.indexOf('=');
            const name = entry.slice(0, split);
            const path = entry.slice(split + 1);
            await page.goto(base + path);
            await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
            const overflow = await page.evaluate(() =>
                Math.max(
                    0,
                    ...[...document.querySelectorAll('html, #root, .ant-layout-content > div')].map(
                        (e) => e.scrollWidth - e.clientWidth,
                    ),
                ),
            );
            const file = `${out}/${name}${labelWidth ? `-${width}` : ''}${suffix}.png`;
            await page.screenshot({ path: file, fullPage: true });
            console.log(`${file}${overflow > 2 ? `  OVERFLOW ${overflow}px` : ''}`);
        }
        await page.close();
    }
    await browser.close();
})();
