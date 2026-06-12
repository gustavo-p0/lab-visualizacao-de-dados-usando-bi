import asyncio
import os
from playwright.async_api import async_playwright

BASE = "http://localhost:8503"
OUT = "prints"

os.makedirs(OUT, exist_ok=True)

CHART_SELECTOR = ".stPlotlyChart, .js-plotly-plot"

async def capture():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 900})

        # Tab 1 - Caracterizacao
        await page.goto(BASE, wait_until="networkidle")
        await page.wait_for_timeout(3000)

        charts = page.locator(".js-plotly-plot")
        n = await charts.count()
        print(f"Tab 1: {n} charts found")

        # Helper to screenshot each chart
        for i in range(n):
            chart = charts.nth(i)
            try:
                box = await chart.bounding_box()
                if box and box["width"] > 100 and box["height"] > 100:
                    name = f"g1_tab1_chart{i}"
                    await chart.screenshot(path=os.path.join(OUT, f"{name}.png"))
                    print(f"  {name}: {box['width']}x{box['height']}")
            except Exception as e:
                print(f"  chart {i}: error - {e}")

        # Tab 2 - RQ1
        tab2 = page.locator('button[data-baseweb="tab"]', has_text="RQ1")
        if await tab2.count() > 0:
            await tab2.first.click()
            await page.wait_for_timeout(4000)

            charts = page.locator(".js-plotly-plot")
            n = await charts.count()
            print(f"Tab 2: {n} charts found")
            for i in range(n):
                chart = charts.nth(i)
                try:
                    box = await chart.bounding_box()
                    if box and box["width"] > 100 and box["height"] > 100:
                        name = f"g2_tab2_chart{i}"
                        await chart.screenshot(path=os.path.join(OUT, f"{name}.png"))
                        print(f"  {name}: {box['width']}x{box['height']}")
                except Exception as e:
                    print(f"  chart {i}: error - {e}")

        # Tab 3 - RQ2
        tab3 = page.locator('button[data-baseweb="tab"]', has_text="RQ2")
        if await tab3.count() > 0:
            await tab3.first.click()
            await page.wait_for_timeout(4000)

            charts = page.locator(".js-plotly-plot")
            n = await charts.count()
            print(f"Tab 3: {n} charts found")
            for i in range(n):
                chart = charts.nth(i)
                try:
                    box = await chart.bounding_box()
                    if box and box["width"] > 100 and box["height"] > 100:
                        name = f"g3_tab3_chart{i}"
                        await chart.screenshot(path=os.path.join(OUT, f"{name}.png"))
                        print(f"  {name}: {box['width']}x{box['height']}")
                except Exception as e:
                    print(f"  chart {i}: error - {e}")

        await browser.close()

asyncio.run(capture())
print("\nDone!")
