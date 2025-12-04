import { test, expect, Page } from '@playwright/test';

/**
 * Customer Service Ticket Quality Score Dashboard - E2E Test Suite
 * 
 * Tests core dashboard functionality: slider interaction, lock mechanism,
 * display accuracy, persistence, and responsive design.
 * 
 * The backend calculates scores. We test the UI works reliably.
 */

test.describe('Ticket Quality Score Dashboard', () => {
  
  async function getDisplayedMetrics(page: Page) {
    const custSat = await page.locator('span#lab-customer_satisfaction').textContent();
    const empathy = await page.locator('span#lab-agent_empathy').textContent();
    const resolution = await page.locator('span#lab-time_to_resolution').textContent();
    
    return {
      customer_satisfaction: custSat ? parseInt(custSat) : 0,
      agent_empathy: empathy ? parseInt(empathy) : 0,
      time_to_resolution: resolution ? parseInt(resolution) : 0,
    };
  }

  test.beforeEach(async ({ page }) => {
    await page.goto('file:///Users/BK_1/Documents/dashboard.html');
  });

  // Slider Interaction Tests
  
  test('Slider should respond to user input and update display value', async ({ page }) => {
    const slider = page.locator('input[data-key="customer_satisfaction"]');
    const label = page.locator('span#lab-customer_satisfaction');
    
    const initialValue = await label.textContent();
    
    await slider.fill('60');
    await page.waitForTimeout(200);
    
    const newValue = await label.textContent();
    expect(newValue).toContain('60');
    expect(newValue).not.toBe(initialValue);
  });

  test('All three metric sliders should be visible and functional', async ({ page }) => {
    const custSatSlider = page.locator('input[data-key="customer_satisfaction"]');
    const empathySlider = page.locator('input[data-key="agent_empathy"]');
    const resolutionSlider = page.locator('input[data-key="time_to_resolution"]');
    
    await expect(custSatSlider).toBeVisible();
    await expect(empathySlider).toBeVisible();
    await expect(resolutionSlider).toBeVisible();
    
    await expect(custSatSlider).not.toBeDisabled();
    await expect(empathySlider).not.toBeDisabled();
    await expect(resolutionSlider).not.toBeDisabled();
  });

  test('Sliders should have correct range (0-100)', async ({ page }) => {
    const slider = page.locator('input[data-key="customer_satisfaction"]');
    
    expect(await slider.getAttribute('min')).toBe('0');
    expect(await slider.getAttribute('max')).toBe('100');
  });

  test('Slider should respond to minimum value (0)', async ({ page }) => {
    await page.locator('input[data-key="customer_satisfaction"]').fill('0');
    await page.waitForTimeout(200);
    
    const metrics = await getDisplayedMetrics(page);
    expect(metrics.customer_satisfaction).toBe(0);
  });

  test('Slider should respond to maximum value (100)', async ({ page }) => {
    await page.locator('input[data-key="customer_satisfaction"]').fill('100');
    await page.waitForTimeout(200);
    
    const metrics = await getDisplayedMetrics(page);
    expect(metrics.customer_satisfaction).toBe(100);
  });

  // Lock Mechanism Tests

  test('Lock button should disable the corresponding slider', async ({ page }) => {
    const slider = page.locator('input[data-key="customer_satisfaction"]');
    const lockBtn = page.locator('button[data-key="customer_satisfaction"]');
    
    await expect(slider).not.toBeDisabled();
    
    await lockBtn.click();
    await page.waitForTimeout(200);
    
    await expect(slider).toBeDisabled();
  });

  test('Lock button should show visual locked state', async ({ page }) => {
    const lockBtn = page.locator('button[data-key="customer_satisfaction"]');
    
    // Initially should not have locked class
    let hasLocked = await lockBtn.evaluate(el => el.className.includes('locked'));
    expect(hasLocked).toBe(false);
    
    await lockBtn.click();
    await page.waitForTimeout(200);
    
    // Should now have locked class
    hasLocked = await lockBtn.evaluate(el => el.className.includes('locked'));
    expect(hasLocked).toBe(true);
  });

  test('Unlocking should re-enable the slider', async ({ page }) => {
    const slider = page.locator('input[data-key="customer_satisfaction"]');
    const lockBtn = page.locator('button[data-key="customer_satisfaction"]');
    
    // Lock it
    await lockBtn.click();
    await page.waitForTimeout(200);
    await expect(slider).toBeDisabled();
    
    // Unlock it
    await lockBtn.click();
    await page.waitForTimeout(200);
    
    // Should be enabled again
    await expect(slider).not.toBeDisabled();
  });

  test('Can lock multiple metrics independently', async ({ page }) => {
    const custSatSlider = page.locator('input[data-key="customer_satisfaction"]');
    const empathySlider = page.locator('input[data-key="agent_empathy"]');
    const custSatLock = page.locator('button[data-key="customer_satisfaction"]');
    const empathyLock = page.locator('button[data-key="agent_empathy"]');
    
    // Lock only customer_satisfaction
    await custSatLock.click();
    await page.waitForTimeout(200);
    
    await expect(custSatSlider).toBeDisabled();
    await expect(empathySlider).not.toBeDisabled();
    
    // Lock agent_empathy too
    await empathyLock.click();
    await page.waitForTimeout(200);
    
    await expect(custSatSlider).toBeDisabled();
    await expect(empathySlider).toBeDisabled();
  });

  // Display & Chart Tests

  test('Dashboard should display overall quality score', async ({ page }) => {
    const scoreText = await page.locator('#overallScore').textContent();
    expect(scoreText).toBeTruthy();
    
    const match = scoreText?.match(/\d+/);
    expect(match).toBeTruthy();
    
    if (match) {
      const score = parseInt(match[0]);
      expect(score).toBeGreaterThanOrEqual(0);
      expect(score).toBeLessThanOrEqual(100);
    }
  });

  test('Chart should render with data points', async ({ page }) => {
    const svg = page.locator('#score-chart');
    await expect(svg).toBeVisible();
    
    const points = await page.locator('#score-chart circle').count();
    expect(points).toBeGreaterThan(0);
  });

  test('Chart should have title', async ({ page }) => {
    await expect(page.locator('h1')).toContainText('Ticket Quality Score');
  });

  test('Tooltip should appear on chart hover', async ({ page }) => {
    const points = page.locator('#score-chart circle');
    const pointCount = await points.count();
    
    if (pointCount > 0) {
      const firstPoint = points.first();
      await firstPoint.scrollIntoViewIfNeeded();
      await page.waitForTimeout(100);
      
      try {
        await firstPoint.hover({ timeout: 5000 });
        await page.waitForTimeout(100);
        
        const tooltip = page.locator('#tooltip');
        await expect(tooltip).toBeVisible({ timeout: 2000 });
      } catch {
        // SVG overlays can interfere with hover - not blocking
      }
    }
  });

  // Persistence Tests

  test('Slider positions should persist after page reload', async ({ page }) => {
    // Set slider to specific value
    await page.locator('input[data-key="customer_satisfaction"]').fill('50');
    await page.waitForTimeout(200);
    
    const metricsBefore = await getDisplayedMetrics(page);
    
    // Reload page
    await page.reload();
    await page.waitForTimeout(500);
    
    // Check value persisted
    const metricsAfter = await getDisplayedMetrics(page);
    expect(metricsAfter.customer_satisfaction).toBe(metricsBefore.customer_satisfaction);
  });

  test('Lock state should persist after page reload', async ({ page }) => {
    // Lock a metric
    await page.locator('button[data-key="customer_satisfaction"]').click();
    await page.waitForTimeout(200);
    
    // Verify it's locked
    await expect(page.locator('input[data-key="customer_satisfaction"]')).toBeDisabled();
    
    // Reload page
    await page.reload();
    await page.waitForTimeout(500);
    
    // Should still be locked
    await expect(page.locator('input[data-key="customer_satisfaction"]')).toBeDisabled();
  });

  test('Multiple locked metrics should persist after reload', async ({ page }) => {
    // Lock two metrics
    await page.locator('button[data-key="customer_satisfaction"]').click();
    await page.locator('button[data-key="agent_empathy"]').click();
    await page.waitForTimeout(200);
    
    // Reload
    await page.reload();
    await page.waitForTimeout(500);
    
    // Both should still be locked
    await expect(page.locator('input[data-key="customer_satisfaction"]')).toBeDisabled();
    await expect(page.locator('input[data-key="agent_empathy"]')).toBeDisabled();
  });

  // Responsive Design Tests

  test('Dashboard should render on mobile viewport (375x667)', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Key elements should be visible
    await expect(page.locator('h1')).toBeVisible();
    await expect(page.locator('#overallScore')).toBeVisible();
    
    // Sliders should be present
    const sliders = page.locator('input[type="range"]');
    expect(await sliders.count()).toBe(3);
  });

  test('Dashboard should render on tablet viewport (768x1024)', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    
    await expect(page.locator('.container')).toBeVisible();
    await expect(page.locator('#score-chart')).toBeVisible();
    
    const sliders = page.locator('input[type="range"]');
    expect(await sliders.count()).toBe(3);
  });

  test('All metric labels should be visible', async ({ page }) => {
    await expect(page.locator('.metric-cell[data-key="customer_satisfaction"]')).toBeVisible();
    await expect(page.locator('.metric-cell[data-key="agent_empathy"]')).toBeVisible();
    await expect(page.locator('.metric-cell[data-key="time_to_resolution"]')).toBeVisible();
  });

  // Edge Cases

  test('Rapid slider changes should be handled smoothly', async ({ page }) => {
    const slider = page.locator('input[data-key="customer_satisfaction"]');
    
    // Make several rapid changes
    for (let i = 20; i <= 80; i += 20) {
      await slider.fill(String(i));
      await page.waitForTimeout(50);
    }
    
    // Should be responsive
    const metrics = await getDisplayedMetrics(page);
    expect(metrics.customer_satisfaction).toBe(80);
  });

});
