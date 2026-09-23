#!/usr/bin/env python3
"""Read-only preview checks; screenshots go to a temporary directory."""
from pathlib import Path
import argparse
import json
import tempfile
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--url', default=(ROOT / 'index.html').as_uri())
    args = p.parse_args()
    out = Path(tempfile.mkdtemp(prefix='ivg-table-review-'))
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=
            '/weka/oe-training-default/jasonr/chenhao_prior/home/.cache/ms-playwright/chromium_headless_shell-1234/chrome-headless-shell-linux64/chrome-headless-shell',
            args=['--no-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 1000}, device_scale_factor=1)
        errors = []
        page.on('pageerror', lambda err: errors.append(str(err)))
        page.goto(args.url)
        page.wait_for_function('Array.from(document.images).every(i => i.complete && i.naturalWidth > 0)')
        assert page.locator('section#task').count() == 1
        page.screenshot(path=str(out/'desktop.png'), full_page=True)
        page.locator('#paper').click()
        assert page.locator('body').evaluate('(el) => el.classList.contains("paper-size")')
        page.locator('#task').screenshot(path=str(out/'paper-width.png'))
        page.locator('#rubric-detail summary').click()
        for key in ['vhhome', 'screensim', 'cooksim']:
            page.locator(f'[data-engine="{key}"]').click()
            page.wait_for_function('document.getElementById("engine-image").complete && document.getElementById("engine-image").naturalWidth > 0')
            assert page.locator('#engine-tex').get_attribute('href') == f'rubric_{key}.tex'
        page.locator('#fit').click()
        page.set_viewport_size({'width':390, 'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth'), 'mobile page overflow'
        page.screenshot(path=str(out/'mobile.png'), full_page=True)
        links = page.locator('a[href]').evaluate_all('(els) => els.map(a => a.getAttribute("href"))')
        for link in links:
            if not link.startswith(('#', 'http')):
                assert (ROOT/link).is_file(), f'Broken local link: {link}'
        assert not errors, errors
        browser.close()
    print(json.dumps({'status':'passed', 'screenshots':str(out), 'links_checked':len(links)}))


if __name__ == '__main__':
    main()
