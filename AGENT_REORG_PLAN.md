# Agent Reorganization Plan - TDD Focus

## Executive Summary

This plan reorganizes 19 agents into **12 laser-focused, TDD-first agents** plus **2 commands**. The reorganization:

1. **Combines similar agents** to reduce redundancy
2. **Separates Django and Vue.js concerns** for clean architecture
3. **Converts utility agents to commands** for better UX
4. **Makes EVERY agent TDD-first** with testing as the primary focus

---

## 🎯 Core Principles

### Test-Driven Development (TDD) First

**Every agent must:**

- Write tests BEFORE implementation
- Follow Red-Green-Refactor cycle
- Achieve minimum 80% coverage
- Include unit, integration, and E2E tests where applicable
- Test security, performance, and edge cases

### Clean Separation of Concerns

- Django agents handle backend only
- Vue.js agents handle frontend only
- Specialized agents for cross-cutting concerns
- No overlap in responsibilities

### Commands vs Agents

- **Commands**: Simple, focused utilities (linting, formatting, policy generation)
- **Agents**: Complex, multi-step development tasks requiring analysis and implementation

---

## 📊 Current State Analysis

### Redundancy Issues

1. **vue3-composition-architect** + **django-vue-api-architect** → Too similar, both handle full-stack
2. **django-db-optimizer** + **django-migration-architect** → Database concerns should be unified
3. **security-reviewer** + **rbac-architect** → Security overlap, RBAC should be part of security
4. **Privacy/ToS generators** → Should be commands, not agents

### Missing TDD Focus

- Only **django-vue-rbac-tester** explicitly focuses on testing
- Other agents mention testing but it's not their primary focus
- No agent enforces TDD methodology consistently

---

## 🔄 Reorganization Strategy

### Phase 1: Consolidation (Combine Similar Agents)

#### 1.1 Django Backend Agent (Combine 4 agents)

**New: `django-tdd-architect`**

- **Combines**: django-db-optimizer + django-migration-architect + django-vue-api-architect (Django parts) + django-vue-refactor (Django parts)
- **Focus**: TDD-first Django backend development
- **Responsibilities**:
  - Write tests FIRST (pytest, Django TestCase)
  - API design and implementation (DRF)
  - Database modeling and migrations
  - Query optimization (N+1, indexing)
  - Backend refactoring
- **TDD Workflow**: Test → Model → Serializer → View → Integration Test → E2E Test

#### 1.2 Vue.js Frontend Agent (Combine 3 agents)

**New: `vue-tdd-architect`**

- **Combines**: vue3-composition-architect + tailwind-ui-ux + django-vue-refactor (Vue parts)
- **Focus**: TDD-first Vue.js development
- **Responsibilities**:
  - Write tests FIRST (Vitest, Vue Test Utils)
  - Component design (Composition API)
  - Tailwind CSS implementation
  - State management (Pinia)
  - Frontend refactoring
- **TDD Workflow**: Test → Component → Composable → Integration Test → E2E Test

#### 1.3 Security & RBAC Agent (Combine 2 agents)

**New: `security-tdd-architect`**

- **Combines**: security-reviewer + rbac-architect
- **Focus**: TDD-first security implementation and auditing
- **Responsibilities**:
  - Write security tests FIRST
  - RBAC system design and implementation
  - Security audits and vulnerability scanning
  - Permission testing (all edge cases)
  - Authentication/authorization testing
- **TDD Workflow**: Security Test → Implementation → Penetration Test → Audit

### Phase 2: Maintain Specialized Agents (8 agents)

These agents remain separate but become **TDD-first**:

#### 2.1 `tdd-test-specialist` (Enhanced django-vue-rbac-tester)

**NEW PRIMARY FOCUS**: Teaching and enforcing TDD methodology

- **Responsibilities**:
  - **Enforce TDD workflow** across all agents
  - Write comprehensive test suites (unit, integration, E2E)
  - Test RBAC and permissions exhaustively
  - Set up CI/CD testing infrastructure
  - Code coverage enforcement (minimum 80%)
  - **Meta-testing**: Tests for the tests
- **TDD Philosophy**: "No code exists until there's a test that needs it"

#### 2.2 `data-tdd-architect` (Enhanced data-architect)

- Write data tests FIRST (schema validation, integrity tests)
- Database design with test-driven constraints
- Data pipeline testing
- Performance benchmarking tests
- Cache validation tests

#### 2.3 `realtime-tdd-architect` (Enhanced realtime-architect)

- WebSocket connection tests FIRST
- Message delivery testing
- Real-time synchronization tests
- Load testing for concurrent connections
- Failure recovery testing

#### 2.4 `async-tdd-architect` (Enhanced async-task-architect)

- Celery task tests FIRST
- Queue behavior testing
- Workflow orchestration tests
- Error handling and retry tests
- Performance and scaling tests

#### 2.5 `observability-tdd-engineer` (Enhanced observability-engineer)

- Monitoring configuration tests FIRST
- Alert rule testing
- Log aggregation validation
- Metric collection tests
- Dashboard functionality tests

#### 2.6 `performance-tdd-optimizer` (Enhanced django-vue-performance-optimizer)

- Performance test suite FIRST
- Benchmark tests (before/after)
- Load testing and stress testing
- Memory leak detection tests
- Bundle size testing

#### 2.7 `devops-tdd-engineer` (Enhanced django-vue-devops)

- Infrastructure tests FIRST
- Deployment pipeline testing
- Docker container tests
- CI/CD validation
- Production smoke tests

#### 2.8 `project-orchestrator` (Enhanced, TDD-aware)

- Coordinates all agents with TDD enforcement
- Ensures test-first approach in all workflows
- Validates test coverage across projects
- No change, already coordination-focused

### Phase 3: Convert to Commands (2 new commands)

#### 3.1 Command: `/lint-and-format`

**Replaces**: lint-format-sorter agent

- **Why**: Simple, deterministic task perfect for a command
- **Usage**: `/lint-and-format [--backend] [--frontend] [--fix]`
- **Actions**:
  - Run Ruff on Django code
  - Run ESLint + Prettier on Vue code
  - Auto-fix issues
  - Report results

#### 3.2 Command: `/generate-legal`

**Replaces**: privacy-policy-generator + terms-of-service-generator agents

- **Why**: Template-based generation, minimal decision-making
- **Usage**: `/generate-legal [privacy|terms|both] --config <config.json>`
- **Actions**:
  - Load configuration
  - Generate documents from templates
  - Output in requested format

---

## 📋 Final Agent Roster (12 Agents + 2 Commands)

### Core Development Agents (TDD-First)

1. **django-tdd-architect** - Django backend with tests first
2. **vue-tdd-architect** - Vue.js frontend with tests first
3. **security-tdd-architect** - Security & RBAC with tests first

### Specialized Agents (TDD-Enhanced)

4. **tdd-test-specialist** - Primary testing agent, enforces TDD methodology
5. **data-tdd-architect** - Data architecture with tests first
6. **realtime-tdd-architect** - Real-time systems with tests first
7. **async-tdd-architect** - Background tasks with tests first
8. **observability-tdd-engineer** - Monitoring with tests first
9. **performance-tdd-optimizer** - Performance with tests first
10. **devops-tdd-engineer** - DevOps with tests first

### Meta Agents

11. **project-orchestrator** - Coordinates all agents (TDD-aware)

### Commands (Not Agents)

- `/lint-and-format` - Code formatting and linting
- `/generate-legal` - Privacy policy and ToS generation

---

## 🔥 TDD-First Implementation for Each Agent

### Standard TDD Workflow (All Agents Follow)

```python
# Every agent follows this pattern:

1. ANALYZE REQUIREMENTS
   - What functionality is needed?
   - What are the edge cases?
   - What could go wrong?

2. WRITE TESTS FIRST (RED)
   - Unit tests for core logic
   - Integration tests for interactions
   - Edge case tests
   - Security tests (if applicable)
   - Performance tests (if applicable)

3. RUN TESTS (FAIL)
   - Verify tests fail appropriately
   - Confirm test assertions are correct

4. IMPLEMENT MINIMUM CODE (GREEN)
   - Write simplest code to pass tests
   - No premature optimization
   - No extra features

5. RUN TESTS (PASS)
   - All tests must pass
   - Coverage must meet minimum threshold

6. REFACTOR (CLEAN)
   - Improve code quality
   - Remove duplication
   - Optimize if needed
   - Tests still pass

7. REPEAT
   - Next feature/requirement
```

### Example: Django TDD Architect Workflow

```python
# User Request: "Create an API endpoint for user profile management"

# STEP 1: Write tests FIRST
"""
tests/test_user_profile_api.py
"""
def test_get_user_profile_authenticated():
    """Test authenticated user can retrieve their profile"""
    # Test code here

def test_get_user_profile_unauthorized():
    """Test unauthorized user gets 401"""
    # Test code here

def test_update_user_profile_valid_data():
    """Test valid profile update"""
    # Test code here

def test_update_user_profile_invalid_email():
    """Test validation catches invalid email"""
    # Test code here

# Run tests → RED (they fail, no implementation yet)

# STEP 2: Implement to pass tests
"""
api/serializers.py
"""
class UserProfileSerializer(serializers.ModelSerializer):
    # Implementation

"""
api/views.py
"""
class UserProfileViewSet(viewsets.ModelViewSet):
    # Implementation

# Run tests → GREEN (tests pass)

# STEP 3: Refactor
# - Optimize queries (select_related)
# - Extract common patterns
# - Clean up code

# Run tests → GREEN (still passing after refactor)
```

### Example: Vue TDD Architect Workflow

```typescript
// User Request: "Create a user profile component"

// STEP 1: Write tests FIRST
// tests/components/UserProfile.test.ts
describe('UserProfile', () => {
  it('displays user information correctly', () => {
    // Test code
  })

  it('shows edit form when edit button clicked', () => {
    // Test code
  })

  it('validates email format before submission', () => {
    // Test code
  })

  it('handles API errors gracefully', () => {
    // Test code
  })
})

// Run tests → RED (component doesn't exist)

// STEP 2: Implement component
// components/UserProfile.vue
<script setup lang="ts">
  // Implementation
</script>

// Run tests → GREEN

// STEP 3: Refactor
// - Extract composables
// - Optimize reactivity
// - Improve Tailwind classes

// Run tests → GREEN
```

---

## 🚀 Migration Plan

### Week 1: Core Agents

- [x] Create `django-tdd-architect` (merge 4 agents)
- [x] Create `vue-tdd-architect` (merge 3 agents)
- [x] Create `security-tdd-architect` (merge 2 agents)
- [x] Enhance `tdd-test-specialist` with TDD enforcement

### Week 2: Specialized Agents

- [ ] Update `data-tdd-architect` with TDD focus
- [ ] Update `realtime-tdd-architect` with TDD focus
- [ ] Update `async-tdd-architect` with TDD focus
- [ ] Update `observability-tdd-engineer` with TDD focus

### Week 3: Final Agents & Commands

- [ ] Update `performance-tdd-optimizer` with TDD focus
- [ ] Update `devops-tdd-engineer` with TDD focus
- [ ] Create `/lint-and-format` command
- [ ] Create `/generate-legal` command

### Week 4: Testing & Documentation

- [ ] Test all agents in real scenarios
- [ ] Update documentation
- [ ] Create TDD training materials
- [ ] Archive old agents

---

## 📈 Success Metrics

### TDD Adoption

- [ ] 100% of code changes have tests written first
- [ ] Minimum 80% test coverage on all new code
- [ ] Zero production bugs from untested code paths
- [ ] All agents follow TDD workflow

### Agent Efficiency

- [ ] 40% reduction in agent count (19 → 12)
- [ ] Clearer separation of concerns
- [ ] Faster task completion (less agent switching)
- [ ] Better test coverage across codebase

### Developer Experience

- [ ] Simpler mental model (Django vs Vue vs Specialized)
- [ ] Commands for simple tasks
- [ ] Agents for complex, multi-step work
- [ ] TDD becomes second nature

---

## 🤔 Decision Points for Review

### Questions for User

1. **Agent Consolidation**: Do you agree with merging:
   - Django agents → `django-tdd-architect`?
   - Vue agents → `vue-tdd-architect`?
   - Security agents → `security-tdd-architect`?

2. **TDD Focus**: Is making TDD the PRIMARY focus acceptable? This means:
   - Tests are ALWAYS written first
   - No implementation without tests
   - 80% coverage minimum enforced

3. **Command Conversion**: Do you agree that linting/formatting and legal doc generation should be commands instead of agents?

4. **Naming**: Preferences on agent names?
   - Current suggestion: `*-tdd-architect` pattern
   - Alternative: `tdd-*-architect` or `*-architect` (TDD implied)

5. **Migration Timeline**: Is 4 weeks reasonable, or do you need faster/slower rollout?

---

## 📝 Next Steps

**After approval of this plan:**

1. I will create the new agent definitions
2. Update agent descriptions with TDD workflows
3. Create migration scripts for legacy agents
4. Build the new commands
5. Test with real-world scenarios
6. Provide updated documentation

**Please review and provide feedback on:**

- Agent consolidations
- TDD-first approach
- Command conversions
- Naming conventions
- Timeline
