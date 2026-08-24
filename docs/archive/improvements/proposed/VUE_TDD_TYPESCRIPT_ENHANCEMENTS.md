# Vue TDD Architect - TypeScript Quality Enhancements

**Proposed by:** Ham Dog & TC
**Date:** 2025-10-16
**Battle-Tested From:** 584 → 111 TypeScript error cleanup (81% reduction)

---

## 🎯 Problem Statement

The `vue-tdd-architect` agent writes comprehensive tests and clean code, BUT it doesn't enforce TypeScript quality standards that prevent the errors we've been fixing.

**Pain Points Discovered:**
1. Test mocks missing required properties (`is_top_agent`, etc.)
2. Template refs accessed without type casting
3. Computed refs mocked with `ref()` instead of `computed()`
4. API client calls without generic types
5. Enum/union types incomplete
6. No pre-commit type checking enforced

**Result:** 584 TypeScript errors accumulated, requiring manual cleanup.

---

## 💡 Proposed Enhancements

### Enhancement 1: Add TypeScript Quality Philosophy

**Insert after line 24 ("Create files with >500 lines of code"):**

```markdown
- **Ship code with ANY TypeScript errors**
- **Use `any` type in production code** (tests are OK with casting)
- **Create test mocks missing required properties**
- **Skip `npm run type-check` before committing**
```

### Enhancement 2: Add TypeScript Quality Standards Section

**Insert after line 25 (before "## 📁 File Organization Rules"):**

```markdown
## 🔒 TypeScript Quality Standards (MANDATORY)

### Rule 1: All Test Mocks Must Match Production Types

**❌ WRONG - Missing required properties:**
```typescript
const mockAgent: AgentProfile = {
  public_id: '123',
  slug: 'test',
  // Missing is_top_agent - TypeScript error!
}
```

**✅ CORRECT - Complete type satisfaction:**
```typescript
const mockAgent: AgentProfile = {
  public_id: '123',
  slug: 'test',
  is_top_agent: false,  // All required fields included
  // ... all other required fields
}
```

**How to prevent:** Before creating mocks, check production type:
```bash
# Find the interface
grep -A 20 "interface AgentProfile" src/modules/agents/types/
# OR hover over type in VSCode to see all fields
```

### Rule 2: Template Refs Must Be Type-Cast in Tests

**❌ WRONG - No type cast:**
```typescript
expect(wrapper.find('[data-test="input"]').element.value).toBe('test')
// Error: Property 'value' does not exist on type 'VueNode<Element>'
```

**✅ CORRECT - Proper type casting:**
```typescript
expect((wrapper.find('[data-test="input"]').element as HTMLInputElement).value).toBe('test')
expect((wrapper.find('[data-test="textarea"]').element as HTMLTextAreaElement).value).toBe('test')
expect((wrapper.find('[data-test="select"]').element as HTMLSelectElement).value).toBe('test')
```

### Rule 3: Component Instance Access Requires Casting

**❌ WRONG - Direct access:**
```typescript
await wrapper.vm.goToStep(1)
expect(wrapper.vm.formData.name).toBe('test')
// Error: Property 'goToStep' does not exist
```

**✅ CORRECT - Cast to any for internal access:**
```typescript
await (wrapper.vm as any).goToStep(1)
expect((wrapper.vm as any).formData.name).toBe('test')
// OK in tests - internal methods not exposed in types
```

**Why this is acceptable:** Test utilities don't expose internal component methods in types. This is a known Vue Test Utils limitation. Using `any` in tests (not production) is the standard practice.

### Rule 4: Mock Computed Properties with `computed()` Not `ref()`

**❌ WRONG - Using ref() for computed:**
```typescript
const createMockComposable = () => ({
  isComplete: ref(false),        // Type error!
  completeness: ref(0),          // Should be ComputedRef
})
```

**✅ CORRECT - Use computed() for computed values:**
```typescript
import { computed } from 'vue'  // Don't forget to import!

const createMockComposable = () => ({
  isComplete: computed(() => false),
  completeness: computed(() => 0),
})
```

**How to know:** Check the real composable's return types:
```bash
tail -20 src/composables/useAgentOnboarding.ts
# If real composable returns computed(), mock returns computed()
```

### Rule 5: API Client Generic Types

**✅ ALWAYS use generic type parameters:**
```typescript
// CORRECT - Type-safe API calls
const user = await api.get<User>('/users/me/')
const response = await api.post<LoginResponse>('/auth/login/', credentials)
const updated = await api.patch<User>('/users/1/', data)
```

**❌ NEVER omit types:**
```typescript
// WRONG - Loses type safety
const user = await api.get('/users/me/')  // Returns any
```

### Rule 6: Enum/Union Type Completeness

**✅ ALWAYS include all possible values:**
```typescript
// CORRECT - Complete union type
export type LeadSource =
  | 'blog'
  | 'social'
  | 'email'
  | 'mortgage_calculator'      // Include ALL calculator sources
  | 'net_proceeds_calculator'
  | 'rent_vs_buy_calculator'
```

**❌ NEVER leave values undefined:**
```typescript
// WRONG - Missing calculator sources
export type LeadSource = 'blog' | 'social' | 'email'
// Using 'mortgage_calculator' will cause TypeScript error
```

### Rule 7: Null/Undefined Handling

**✅ ALWAYS explicitly handle undefined:**
```typescript
// CORRECT - Convert undefined to null if needed
formData.recurrence = pattern ?? null
formData.value = data?.value ?? ''
```

**❌ NEVER leave undefined ambiguity:**
```typescript
// WRONG - Type mismatch
const pattern: RecurrencePattern | null | undefined = getPattern()
formData.recurrence = pattern  // Error: undefined not assignable to null
```

### Rule 8: Module Import Paths

**✅ ALWAYS verify component locations before importing:**
```typescript
// Step 1: Check if component exists
// ls src/modules/agents/components/agents/

// Step 2: Use correct path
import AgentsGrid from '@/modules/default/components/agents/AgentsGrid.vue'
```

**❌ NEVER assume component location:**
```typescript
// WRONG - Component may not exist here
import AgentsGrid from '../../components/agents/AgentsGrid.vue'
```

## 📋 Pre-Commit TypeScript Checklist

Before committing ANY code, verify:

```bash
# 1. Type check passes
npm run type-check
# Must show: No errors found

# 2. Lint passes
npm run lint
# Must show: 0 errors

# 3. Tests pass
npm run test:unit
# All tests green

# 4. Build succeeds
npm run build-only
# No build errors
```

**If ANY of these fail, DO NOT COMMIT.**

## 🔍 TypeScript Error Prevention Workflow

### Before Creating Test Mocks

```typescript
// STEP 1: Check the production type definition
// grep -A 20 "interface AgentProfile" src/modules/agents/types/
// OR hover over type in VSCode to see full interface

// STEP 2: List ALL required properties
// Make a checklist of every required field

// STEP 3: Create complete mock
const mockAgent: AgentProfile = {
  // Include EVERY required field from step 2
  public_id: '123',
  slug: 'test',
  is_top_agent: false,
  // ... all other required fields
}

// STEP 4: Verify no TypeScript errors
// npm run type-check should pass
```

### Before Accessing Template Refs

```typescript
// STEP 1: Identify HTML element type
// <input> → HTMLInputElement
// <textarea> → HTMLTextAreaElement
// <select> → HTMLSelectElement
// <button> → HTMLButtonElement
// <div> → HTMLDivElement

// STEP 2: Cast appropriately
const element = wrapper.find('[data-test="input"]').element as HTMLInputElement
expect(element.value).toBe('test')
```

### Before Creating Composable Mocks

```typescript
// STEP 1: Check real composable return type
// tail -20 src/composables/useAgentOnboarding.ts

// STEP 2: Match return structure EXACTLY
// If real composable returns computed(), mock returns computed()
// If real composable returns ref(), mock returns ref()

const createMock = () => ({
  // Match real composable's reactive types
  isComplete: computed(() => false),  // Real is computed
  formData: ref({}),                  // Real is ref
})
```

## 🎓 Reference Documentation

When stuck on TypeScript errors, refer to:
- **Project-specific**: `frontend/TYPESCRIPT_PATTERNS.md` - Battle-tested solutions
- **Diagnostic command**: `npm run type-check 2>&1 | grep "error TS" | cut -d: -f3- | sort | uniq -c | sort -rn`
- **Fix strategy**: Always fix highest-count error categories first
```

---

## 🔄 Modified TDD Workflow

### Updated Step 1: Analyze & Plan Tests (RED Phase Prep)

**CHANGE lines 459-468 to:**

```typescript
// Before ANY code, you ask:
1. What exactly needs to render?
2. What user interactions must work?
3. What edge cases exist?
4. What API calls are needed?
5. What loading/error states matter?
6. **What TypeScript types are involved?** ← NEW
7. **Do all required properties exist in mocks?** ← NEW
8. **Are template refs properly type-cast?** ← NEW

// Then you write the test plan WITH proper types
```

### Updated Step 2: Write Tests FIRST (NEW Pattern)

**ADD to line 470 (before example code):**

```markdown
**TypeScript-Clean Test Pattern:**

1. Import proper types: `import type { User } from '@/types/user'`
2. Import `computed` if mocking composables: `import { computed } from 'vue'`
3. Create complete mocks with all required fields
4. Cast template refs to proper HTML types
5. Cast `wrapper.vm` for internal access

**Example with all TypeScript patterns:**
```

**Then show the ENHANCED example code (add to existing example):**

```typescript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { computed } from 'vue'  // ✅ Import for mocks
import UserProfile from '../UserProfile.vue'
import { useUserStore } from '@/stores/user'
import type { User } from '@/types/user'  // ✅ Import types

describe('UserProfile', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders user information when loaded', async () => {
    // ✅ Complete mock with ALL required properties
    const mockUser: User = {
      id: 1,
      public_id: 'user-1',
      name: 'John Doe',
      email: 'john@example.com',
      is_active: true,
      is_staff: false,
      date_joined: '2024-01-01T00:00:00Z',
      last_login: '2024-01-15T00:00:00Z',
    }

    const wrapper = mount(UserProfile, {
      props: { userId: 1 }
    })

    const userStore = useUserStore()
    userStore.currentUser = mockUser

    await wrapper.vm.$nextTick()

    expect(wrapper.find('[data-test="user-name"]').text()).toBe('John Doe')
  })

  it('validates email input with proper type casting', async () => {
    const wrapper = mount(UserProfile, {
      props: { userId: 1 }
    })

    await (wrapper.vm as any).openEditMode()  // ✅ Cast for internal method

    // ✅ Type-safe element casting
    const emailInput = wrapper.find('[data-test="email-input"]').element as HTMLInputElement
    emailInput.value = 'invalid-email'
    await emailInput.dispatchEvent(new Event('input'))

    const saveButton = wrapper.find('[data-test="save-button"]')
    await saveButton.trigger('click')

    expect(wrapper.find('[data-test="email-error"]').text()).toContain('Invalid')
  })
})

// ✅ Composable mock with computed refs
const createMockComposable = (overrides = {}) => ({
  isComplete: computed(() => false),  // Use computed, not ref!
  completeness: computed(() => 0),
  ...overrides,
})
```

### Updated Step 5: Add Type Check (NEW STEP)

**INSERT after Step 5 (line 852), BEFORE Step 6:**

```markdown
### Step 5.5: Run Type Check (Confirm TypeScript Clean)

```bash
# ✅ CRITICAL: Run type check
npm run type-check

# Expected output:
# No errors found

# If you see errors:
npm run type-check 2>&1 | grep "error TS" | head -20
# Fix ALL errors before proceeding

# This is MANDATORY - no exceptions!
```

**Why this step matters:**
- Tests passing doesn't mean types are clean
- TypeScript errors block CI/CD
- Prevents tech debt accumulation
- Catches type issues before they compound

**If type check fails:**
1. Check test mocks have all required properties
2. Verify template refs are type-cast
3. Ensure API calls use generic types
4. Fix errors using patterns from `frontend/TYPESCRIPT_PATTERNS.md`
```

### Updated Step 7: Final Verification

**CHANGE line 922-928 to:**

```bash
# All FOUR checks MUST pass
npm run test:unit && npm run type-check && npm run lint && npm run build-only

# If ALL pass:
# ✅ READY TO COMMIT

# If ANY fail:
# ❌ FIX BEFORE COMMITTING - NO EXCEPTIONS
```

---

## ✅ Success Criteria Enhancement

**REPLACE line 1481-1491 with:**

```markdown
## 📊 Success Criteria

Every Vue task you complete must have:

- ✅ Tests written BEFORE implementation
- ✅ All tests passing (green)
- ✅ **TypeScript type-check passes with 0 errors** ← NEW
- ✅ **ESLint passes with 0 errors** ← NEW
- ✅ 85%+ code coverage
- ✅ User interaction tests included
- ✅ Accessibility tested
- ✅ Edge cases covered
- ✅ Tailwind classes tested
- ✅ **Build succeeds (`npm run build-only`)** ← NEW
- ✅ **All test mocks have complete type properties** ← NEW
- ✅ **Template refs properly type-cast** ← NEW
- ✅ **API calls use generic types** ← NEW

**If even ONE checkbox fails, the task is NOT complete.**
```

---

## 🔄 Updated Description

**CHANGE line 3 (agent description) to:**

```markdown
description: Elite Vue 3 Composition API architect specializing in Test-Driven Development. Writes comprehensive tests FIRST using Vitest and Vue Test Utils, then implements components, composables, Pinia stores, and Tailwind styling. Enforces Red-Green-Refactor cycle AND TypeScript quality standards for all frontend code. NO TypeScript errors allowed - every commit is type-clean.
```

---

## 📝 Implementation Plan

### Phase 1: Review & Approve (YOU DO THIS)
- [ ] Review this enhancement proposal
- [ ] Approve or request changes
- [ ] TC implements changes

### Phase 2: Apply Enhancements (TC DOES THIS)
- [ ] Backup current agent file
- [ ] Apply enhancements to `vue-tdd-architect.md`
- [ ] Test agent with a small task
- [ ] Verify it enforces TypeScript quality

### Phase 3: Validate (WE DO TOGETHER)
- [ ] Run agent on a test component
- [ ] Verify it catches TypeScript issues
- [ ] Measure error prevention effectiveness

---

## 🎯 Expected Impact

**Before Enhancement:**
- Agent writes clean tests + code
- TypeScript errors accumulate
- Manual cleanup required
- 584 errors accumulated

**After Enhancement:**
- Agent writes clean tests + type-safe code
- TypeScript errors prevented at source
- Zero manual TypeScript cleanup
- CI/CD stays green

**Time Saved:** ~4-6 hours per sprint (no more TypeScript cleanup sessions)

---

## 💭 Ham Dog's Decision

**Option A:** Approve as-is - TC implements all enhancements
**Option B:** Request modifications - specify what to change
**Option C:** Reject - keep current agent, rely on manual vigilance

**What's your call, Ham Dog?** 🤔
