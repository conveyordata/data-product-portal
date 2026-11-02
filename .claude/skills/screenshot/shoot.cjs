const { chromium } = require('playwright');

const [base, out, suffix, ...pages] = process.argv.slice(2);

(async () => {
    const browser = await chromium.launch({ args: ['--disable-web-security'] });
    const page = await browser.newPage({ viewport: { width: 1440, height: 1300 } });
    for (const entry of pages) {
        const [name, path] = entry.split('=');
        await page.goto(base + path);
        await page.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
        await page.screenshot({ path: `${out}/${name}${suffix}.png`, fullPage: true });
        console.log(`${out}/${name}${suffix}.png`);
    }
    await browser.close();
})();
