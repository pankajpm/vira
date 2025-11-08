# VIRA Chainlit UI - Testing Checklist

**Before Deploying to Production**

---

## Pre-Test Setup

```bash
# 1. Ensure dependencies are installed
pip install -e .

# 2. Verify environment variables
cat .env | grep OPENAI_API_KEY
# Should show: OPENAI_API_KEY=sk-...

# 3. Check vector database exists
ls -la ./data/processed/chroma/
# Should show: chroma.sqlite3 and UUID directories

# 4. Start the application
./start_chainlit_ui.sh
# Should open on http://localhost:8000
```

---

## Test Suite

### 🟢 Phase 1: Basic Functionality

**Test 1.1: Fresh Installation**
- [ ] App starts without errors
- [ ] Welcome message appears
- [ ] Asked for company name
- [ ] Company name is saved
- [ ] Session ID visible in logs

**Test 1.2: Business Plan Editor**
- [ ] Click "✏️ Edit Plan" button
- [ ] Modal/dialog appears for input
- [ ] Paste sample plan (see below)
- [ ] Save confirmation message appears
- [ ] Version number shown (v1)

**Sample Business Plan:**
```
Company: HealthTech AI

Problem: Hospitals struggle with diagnostic delays
Solution: AI-powered diagnostic assistant
Market: $50B healthcare AI market
Team: Ex-Google engineers with ML expertise
Traction: 5 design partners, pre-revenue
Stage: Seeking Series A ($15M)
Location: Austin, Texas
```

**Test 1.3: Analysis Execution**
- [ ] Click "🔍 Analyze" button
- [ ] Step-by-step progress shown:
  - [ ] "📚 Retrieving VC criteria"
  - [ ] "🤖 Generating analysis"
- [ ] Analysis results appear within 5 seconds
- [ ] Results show:
  - [ ] Company name header
  - [ ] 3-5 Alignment items
  - [ ] 3-5 Gap items
  - [ ] Summary paragraph
  - [ ] Source URLs cited

**Test 1.4: Command Interface**
- [ ] Type `/analyze` in chat
- [ ] Same analysis runs as button click
- [ ] Type `analyze` (without slash)
- [ ] Also triggers analysis

---

### 🟡 Phase 2: Session Persistence

**Test 2.1: Page Refresh**
- [ ] Complete Test 1.1-1.3 above
- [ ] Refresh browser (Cmd+R or F5)
- [ ] Session persists (no re-prompt for company name)
- [ ] Chat history visible
- [ ] Business plan still accessible

**Test 2.2: Browser Close & Reopen**
- [ ] Complete a full session
- [ ] Close browser completely
- [ ] Reopen http://localhost:8000
- [ ] Settings → Session dropdown shows previous session
- [ ] Select previous session
- [ ] All history restored

**Test 2.3: Multiple Sessions**
- [ ] Create Session 1 (Company A)
- [ ] Add plan, run analysis
- [ ] Settings → Session → "➕ Start New Session"
- [ ] Create Session 2 (Company B)
- [ ] Add different plan, run analysis
- [ ] Switch back to Session 1 via dropdown
- [ ] Verify correct plan and history loaded
- [ ] Switch to Session 2
- [ ] Verify correct plan and history loaded

---

### 🔵 Phase 3: Version Control

**Test 3.1: Plan Editing**
- [ ] Save initial plan (v1)
- [ ] Click "✏️ Edit Plan"
- [ ] Modify plan (add new section)
- [ ] Save → Confirmation shows v2
- [ ] Diff summary shown (e.g., "+3 lines, -0 lines")

**Test 3.2: Version History**
- [ ] Create 3 versions of plan
- [ ] Click "📜 Versions" button
- [ ] All 3 versions listed
- [ ] Each shows:
  - [ ] Version number
  - [ ] Timestamp
  - [ ] Created by (user/system)
  - [ ] Diff summary
  - [ ] Content preview

**Test 3.3: Analysis with Different Versions**
- [ ] Save plan v1 → Analyze → Note results
- [ ] Edit plan → Save v2 → Analyze → Note results
- [ ] Verify results differ based on plan changes

---

### 🟣 Phase 4: Debug Mode

**Test 4.1: Enable Debug Mode**
- [ ] Settings → Toggle "🔧 Developer Mode" ON
- [ ] Run analysis
- [ ] Debug panel appears below results
- [ ] Shows sections:
  - [ ] Performance (retrieval/LLM/total ms)
  - [ ] Retrieved Documents (with URLs)
  - [ ] Tokens & Cost
  - [ ] Tracing (LangSmith link or placeholder)

**Test 4.2: Debug Metrics Accuracy**
- [ ] Total time shown is reasonable (2-5 seconds)
- [ ] Retrieval time < LLM time
- [ ] Document count matches (typically 6-8)
- [ ] Document URLs are valid a16z.com links
- [ ] Preview text makes sense

**Test 4.3: Disable Debug Mode**
- [ ] Settings → Toggle debug mode OFF
- [ ] Run analysis
- [ ] No debug panel appears
- [ ] Analysis results still shown

---

### 🟠 Phase 5: Error Handling

**Test 5.1: Analyze Without Plan**
- [ ] Create new session
- [ ] Immediately click "🔍 Analyze" (no plan saved)
- [ ] Warning message appears:
  - [ ] "⚠️ No business plan found..."
- [ ] Does NOT crash

**Test 5.2: Empty Plan**
- [ ] Edit plan → Enter just whitespace → Save
- [ ] Click Analyze
- [ ] Handled gracefully (error or empty analysis)

**Test 5.3: Very Long Plan**
- [ ] Paste 10,000+ word business plan
- [ ] Save successfully
- [ ] Analysis runs without timeout
- [ ] Results still coherent

**Test 5.4: Invalid Session**
- [ ] Manually set invalid session_id in browser console:
  ```javascript
  // Open browser console
  localStorage.setItem('chainlit-session', 'invalid-uuid')
  ```
- [ ] Refresh page
- [ ] Error handled gracefully
- [ ] Option to start new session

**Test 5.5: Database Locked**
- [ ] Open database in another tool:
  ```bash
  sqlite3 ./data/vira_sessions.db
  # Leave terminal open
  ```
- [ ] Try to save plan in UI
- [ ] Should show error or retry
- [ ] Close sqlite3 session
- [ ] Try again → Should work

---

### 🔴 Phase 6: Performance

**Test 6.1: Cold Start**
- [ ] Stop application
- [ ] Start application
- [ ] Measure time to first welcome message
- [ ] Should be < 3 seconds

**Test 6.2: Query Latency**
- [ ] Time 5 consecutive analyses
- [ ] Record times:
  1. _____ seconds
  2. _____ seconds
  3. _____ seconds
  4. _____ seconds
  5. _____ seconds
- [ ] Average should be 2-4 seconds
- [ ] No significant degradation over time

**Test 6.3: Database Size**
- [ ] Check initial DB size:
  ```bash
  ls -lh ./data/vira_sessions.db
  ```
- [ ] Create 10 sessions with analyses
- [ ] Check new DB size
- [ ] Growth should be ~100-200 KB

**Test 6.4: Memory Usage**
- [ ] Monitor memory (Activity Monitor / Task Manager)
- [ ] Start application → Note memory
- [ ] Run 20 analyses → Note memory
- [ ] Should stay under 500 MB

---

### ⚫ Phase 7: Edge Cases

**Test 7.1: Special Characters**
- [ ] Company name: "Acme™ & Co. (ÜK) Ltd."
- [ ] Plan with emojis: "🚀 Our mission..."
- [ ] All save and display correctly

**Test 7.2: Concurrent Sessions**
- [ ] Open UI in two browser tabs
- [ ] Create different sessions in each
- [ ] Verify no cross-contamination
- [ ] Both work independently

**Test 7.3: Rapid Clicking**
- [ ] Click "Analyze" button 5 times rapidly
- [ ] Should either:
  - [ ] Queue requests, or
  - [ ] Prevent duplicate submissions
- [ ] No crashes

**Test 7.4: Network Interruption**
- [ ] Start analysis
- [ ] Disconnect internet mid-analysis
- [ ] Should show error message
- [ ] Reconnect internet
- [ ] Retry → Should work

---

## Database Verification

After completing all tests, verify database integrity:

```bash
sqlite3 ./data/vira_sessions.db

-- Check table counts
SELECT COUNT(*) FROM sessions;
SELECT COUNT(*) FROM messages;
SELECT COUNT(*) FROM business_plans;
SELECT COUNT(*) FROM analyses;

-- Verify relationships
SELECT s.company_name, COUNT(m.id) as msg_count, COUNT(DISTINCT bp.version) as versions
FROM sessions s
LEFT JOIN messages m ON s.id = m.session_id
LEFT JOIN business_plans bp ON s.id = bp.session_id
GROUP BY s.id;

-- Check for orphaned records (should return 0)
SELECT COUNT(*) FROM messages WHERE session_id NOT IN (SELECT id FROM sessions);
SELECT COUNT(*) FROM business_plans WHERE session_id NOT IN (SELECT id FROM sessions);
SELECT COUNT(*) FROM analyses WHERE session_id NOT IN (SELECT id FROM sessions);
```

Expected:
- [ ] No orphaned records
- [ ] Counts match your test sessions
- [ ] All foreign keys valid

---

## Known Issues to Ignore

1. **"No left sidebar"** - Chainlit limitation, use dropdown instead
2. **"LangSmith trace says 'not enabled'"** - Integration TODO
3. **"Token counts show 0"** - Calculation TODO
4. **"Modal editor not inline"** - Chainlit component limitation

These are documented in `CHAINLIT_IMPLEMENTATION_SUMMARY.md` as future work.

---

## Acceptance Criteria

For production deployment, ensure:

- [x] All Phase 1-3 tests pass (basic functionality)
- [x] Phase 4 passes (debug mode works)
- [x] Phase 5 passes (no crashes on errors)
- [ ] Phase 6 passes (performance acceptable)
- [ ] Phase 7 passes (edge cases handled)
- [ ] Database verification shows no issues
- [ ] No Python exceptions in terminal logs
- [ ] No JavaScript errors in browser console

---

## Reporting Issues

If tests fail, collect:

1. **Terminal logs** - Copy full error stack trace
2. **Browser console** - F12 → Console tab → Copy errors
3. **Database state** - Run queries above
4. **Steps to reproduce** - Exact sequence of actions
5. **Environment** - Python version, OS, browser

File bug report with all information above.

---

## Performance Benchmarks

Expected values for reference:

| Metric | Target | Acceptable | Poor |
|--------|--------|------------|------|
| **Cold Start** | < 2s | < 3s | > 5s |
| **Analysis Time** | 2-3s | 3-5s | > 5s |
| **Retrieval** | 100-200ms | 200-400ms | > 500ms |
| **LLM Generation** | 2-3s | 3-4s | > 5s |
| **Message Save** | < 50ms | < 100ms | > 200ms |
| **Session Load** | < 100ms | < 200ms | > 500ms |

---

## Next Steps After Testing

Once all tests pass:

1. **Document findings** - Create summary report
2. **Fix critical bugs** - Anything that crashes app
3. **Optimize bottlenecks** - If performance is "Poor"
4. **User acceptance testing** - Get real user feedback
5. **Plan agentic backend** - Begin Iteration 2

---

**Testing Time Estimate:** 1-2 hours for comprehensive coverage

**Status Tracking:**
- [ ] Phase 1: Basic Functionality
- [ ] Phase 2: Session Persistence
- [ ] Phase 3: Version Control
- [ ] Phase 4: Debug Mode
- [ ] Phase 5: Error Handling
- [ ] Phase 6: Performance
- [ ] Phase 7: Edge Cases
- [ ] Database Verification
- [ ] Acceptance Criteria Met

**Tester:** _____________  
**Date:** _____________  
**Result:** ⬜ PASS | ⬜ FAIL | ⬜ CONDITIONAL

