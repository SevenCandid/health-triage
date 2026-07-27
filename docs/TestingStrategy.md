# Testing & Quality Assurance Strategy

## 1. Full-Spectrum Testing Pyramid

The **Health Triage Assistant** employs a 4-tier testing strategy to ensure zero clinical defects, 100% offline reliability, and fast API execution.

```
                  / \
                 /   \  End-to-End Tests (Playwright / Offline Emulation)
                /-----\
               /       \  Integration Tests (FastAPI + Async PostgreSQL)
              /---------\
             /           \  Clinical Rule Benchmark Tests (MTS Verification)
            /-------------\
           /               \  Unit Tests (Pytest Domain & Vitest Components)
          /-----------------\
```

---

## 2. Unit & Integration Testing (Backend - Pytest)

### Test Scope:
- **Domain Rule Evaluator**: Validates decision tree transitions against edge-case symptom permutations.
- **SQLAlchemy Repositories**: Validates async database operations using an in-memory SQLite database (`sqlite+aiosqlite`).
- **FastAPI Endpoints**: Validates request/response validation using `httpx.AsyncClient`.

```python
# Sample Pytest Test Case Signature
@pytest.mark.asyncio
async def test_triage_red_flag_override(async_client: AsyncClient):
    payload = {
        "primarySymptom": "chest_pain",
        "patientAge": 45,
        "answers": {"q_shortness_of_breath": "yes"}
    }
    response = await async_client.post("/api/v1/triage/evaluate", json=payload)
    assert response.status_code == 200
    assert response.json()["urgencyLevel"] == "RED"
```

---

## 3. Frontend Unit & Component Testing (Vitest + Testing Library)

### Test Scope:
- **Client Rule Engine JS**: Validates 100% accurate rule evaluation offline.
- **Zustand Stores**: Verifies state mutations for language toggle and active session updates.
- **TriageCard Rendering**: Asserts correct accessibility labels and CSS urgency colors (`RED`, `ORANGE`, `YELLOW`, `GREEN`).

---

## 4. End-to-End (E2E) & Offline Emulation Testing (Playwright)

Playwright tests simulate real mobile devices under varying network conditions:

```typescript
// Sample Playwright Offline E2E Test
test('should complete full triage flow while completely offline', async ({ page, context }) => {
  await page.goto('http://localhost:3000');
  
  // 1. Simulate Offline Network Disconnect
  await context.setOffline(true);
  
  // 2. Interact with App
  await page.click('text=Start Triage');
  await page.click('text=Fever');
  await page.click('button:has-text("Submit")');
  
  // 3. Verify Offline Triage Card Rendered
  await expect(page.locator('.triage-card')).toBeVisible();
  await expect(page.locator('.triage-badge')).toHaveText(/YELLOW|ORANGE|RED|GREEN/);
});
```

---

## 5. Clinical Decision Tree Validation Suite

A dedicated automated test suite runs **200+ standardized clinical patient case studies** against the decision tree rules to ensure zero false-negative classifications (e.g., ensuring a true cardiac event is never misclassified as GREEN or YELLOW).
