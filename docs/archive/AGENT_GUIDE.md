# Agent Ecosystem Guide

**Version**: 1.0.0
**Updated**: 2025-11-26
**Total Agents**: 26

## Quick Agent Selection

### By Task Type

| Task | Primary Agent | Supporting Agents |
|------|--------------|-------------------|
| **Django API Development** | `django-tdd-architect` | `django-data-architect`, `django-security-architect` |
| **FastAPI Development** | `fastapi-tdd-architect` | `fastapi-data-architect`, `fastapi-security-architect` |
| **Vue.js Frontend** | `vue-tdd-architect` | `e2e-tdd-architect`, `performance-tdd-optimizer` |
| **React Native Mobile** | `react-native-tdd-architect` | `mobile-data-architect`, `mobile-security-architect` |
| **Database Design** | `data-tdd-architect` | Framework-specific data agent |
| **Security Implementation** | `security-tdd-architect` | Framework-specific security agent |
| **Background Jobs** | `async-tdd-architect` | `observability-tdd-engineer` |
| **Real-time Features** | `realtime-tdd-architect` | `mobile-realtime-architect` (mobile) |
| **E2E Testing** | `e2e-tdd-architect` | `tdd-test-specialist` |
| **Performance Optimization** | `performance-tdd-optimizer` | `mobile-performance-optimizer` (mobile) |
| **DevOps/Deployment** | `devops-tdd-engineer` | Staging agents |
| **Monitoring/Observability** | `observability-tdd-engineer` | `devops-tdd-engineer` |
| **Native Modules** | `native-module-tdd-engineer` | `react-native-tdd-architect` |
| **App Store Deployment** | `expo-deployment-agent` | `devops-tdd-engineer` |
| **Complex Orchestration** | `project-orchestrator` | All relevant domain agents |
| **Test Review/Enforcement** | `tdd-test-specialist` | All agents |

### By Stack

#### Django + Vue.js Stack
```
Primary:     django-tdd-architect, vue-tdd-architect
Data:        django-data-architect
Security:    django-security-architect
Async:       async-tdd-architect
Real-time:   realtime-tdd-architect
Staging:     django-vue-staging-agent
Testing:     e2e-tdd-architect, tdd-test-specialist
Monitoring:  observability-tdd-engineer
DevOps:      devops-tdd-engineer
```

#### FastAPI + Vue.js Stack
```
Primary:     fastapi-tdd-architect, vue-tdd-architect
Data:        fastapi-data-architect
Security:    fastapi-security-architect
Async:       async-tdd-architect
Real-time:   realtime-tdd-architect
Staging:     fastapi-vue-staging-agent
Testing:     e2e-tdd-architect, tdd-test-specialist
Monitoring:  observability-tdd-engineer
DevOps:      devops-tdd-engineer
```

#### React Native Mobile Stack
```
Primary:     react-native-tdd-architect
Data:        mobile-data-architect
Security:    mobile-security-architect
Real-time:   mobile-realtime-architect
Performance: mobile-performance-optimizer
Native:      native-module-tdd-engineer
Deployment:  expo-deployment-agent
Testing:     e2e-tdd-architect, tdd-test-specialist
Monitoring:  observability-tdd-engineer
```

---

## Agent Dependency Graph

```
                    ┌─────────────────────────┐
                    │   project-orchestrator  │
                    │    (Master Conductor)   │
                    └───────────┬─────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
        ▼                       ▼                       ▼
┌───────────────┐      ┌───────────────┐      ┌───────────────┐
│ tdd-test-     │      │ observability-│      │ devops-tdd-   │
│ specialist    │      │ tdd-engineer  │      │ engineer      │
│ (Quality)     │      │ (Monitoring)  │      │ (Infra)       │
└───────┬───────┘      └───────┬───────┘      └───────┬───────┘
        │                      │                      │
        │      ALL AGENTS REFERENCE THESE THREE      │
        │                      │                      │
┌───────┴──────────────────────┴──────────────────────┴───────┐
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              FRAMEWORK LAYER                         │    │
│  │                                                      │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │    │
│  │  │   Django     │  │   FastAPI    │  │  Vue.js   │  │    │
│  │  │              │  │              │  │           │  │    │
│  │  │ tdd-architect│  │ tdd-architect│  │tdd-archite│  │    │
│  │  │ data-arch    │  │ data-arch    │  │           │  │    │
│  │  │ security-arch│  │ security-arch│  │           │  │    │
│  │  └──────────────┘  └──────────────┘  └───────────┘  │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │              MOBILE LAYER                     │   │    │
│  │  │                                               │   │    │
│  │  │  react-native-tdd-architect (core)           │   │    │
│  │  │       │                                       │   │    │
│  │  │       ├── mobile-data-architect              │   │    │
│  │  │       ├── mobile-security-architect          │   │    │
│  │  │       ├── mobile-realtime-architect          │   │    │
│  │  │       ├── mobile-performance-optimizer       │   │    │
│  │  │       ├── native-module-tdd-engineer         │   │    │
│  │  │       └── expo-deployment-agent              │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │           CROSS-CUTTING LAYER                 │   │    │
│  │  │                                               │   │    │
│  │  │  data-tdd-architect ──► django/fastapi-data  │   │    │
│  │  │  security-tdd-architect ──► django/fastapi/  │   │    │
│  │  │                           mobile-security    │   │    │
│  │  │  realtime-tdd-architect ──► mobile-realtime  │   │    │
│  │  │  performance-tdd-optimizer ──► mobile-perf   │   │    │
│  │  │  async-tdd-architect (Celery tasks)          │   │    │
│  │  │  e2e-tdd-architect (Playwright)              │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  │                                                      │    │
│  │  ┌──────────────────────────────────────────────┐   │    │
│  │  │           DEPLOYMENT LAYER                    │   │    │
│  │  │                                               │   │    │
│  │  │  django-vue-staging-agent                    │   │    │
│  │  │  fastapi-vue-staging-agent                   │   │    │
│  │  │  expo-deployment-agent                       │   │    │
│  │  └──────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### Agent Relationships

| Agent | Depends On | Is Dependency For |
|-------|------------|-------------------|
| `project-orchestrator` | All agents | - |
| `tdd-test-specialist` | - | All agents |
| `observability-tdd-engineer` | - | All agents |
| `devops-tdd-engineer` | - | All staging/deployment agents |
| `django-tdd-architect` | `tdd-test-specialist` | `django-data-architect`, `django-security-architect` |
| `fastapi-tdd-architect` | `tdd-test-specialist` | `fastapi-data-architect`, `fastapi-security-architect` |
| `react-native-tdd-architect` | `tdd-test-specialist` | All mobile agents |
| `data-tdd-architect` | - | `django-data-architect`, `fastapi-data-architect`, `mobile-data-architect` |
| `security-tdd-architect` | - | `django-security-architect`, `fastapi-security-architect`, `mobile-security-architect` |

---

## Common Patterns Library

### TDD Test File Pattern

```python
# ALWAYS use this structure for test files
# File: tests/<domain>/test_<feature>.py

import pytest
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from <domain>.models import <Model>

# === FIXTURES ===
@pytest.fixture
def sample_data() -> dict:
    """Fixture providing test data"""
    return {"key": "value"}

# === UNIT TESTS ===
class TestFeatureName:
    """Tests for <feature>"""

    def test_happy_path(self, sample_data):
        """Should succeed with valid input"""
        pass

    def test_edge_case(self):
        """Should handle edge case"""
        pass

    def test_error_handling(self):
        """Should raise appropriate error"""
        pass
```

### Mock Pattern

```python
# File: tests/conftest.py
import pytest
from unittest.mock import MagicMock, AsyncMock, patch

@pytest.fixture
def mock_external_service():
    """Mock external API calls"""
    with patch('module.external_service') as mock:
        mock.return_value = {"status": "success"}
        yield mock

@pytest.fixture
def mock_async_service():
    """Mock async external calls"""
    with patch('module.async_service', new_callable=AsyncMock) as mock:
        mock.return_value = {"status": "success"}
        yield mock
```

### API Test Pattern

```python
# Django REST Framework
@pytest.mark.django_db
class TestAPIEndpoint:
    def test_list_authenticated(self, api_client, user):
        api_client.force_authenticate(user=user)
        response = api_client.get('/api/v1/resource/')
        assert response.status_code == 200

# FastAPI
@pytest.mark.asyncio
async def test_endpoint(async_client, auth_headers):
    response = await async_client.get('/api/v1/resource/', headers=auth_headers)
    assert response.status_code == 200
```

### Component Test Pattern (Vue/React Native)

```typescript
// Vue.js with Vitest
import { describe, it, expect } from 'vitest';
import { mount } from '@vue/test-utils';

describe('ComponentName', () => {
  it('renders correctly', () => {
    const wrapper = mount(Component, { props: { value: 'test' } });
    expect(wrapper.text()).toContain('test');
  });

  it('emits event on click', async () => {
    const wrapper = mount(Component);
    await wrapper.find('button').trigger('click');
    expect(wrapper.emitted('click')).toBeTruthy();
  });
});

// React Native with Jest
import { render, fireEvent } from '@testing-library/react-native';

describe('ComponentName', () => {
  it('renders correctly', () => {
    const { getByText } = render(<Component value="test" />);
    expect(getByText('test')).toBeTruthy();
  });

  it('calls handler on press', () => {
    const onPress = jest.fn();
    const { getByRole } = render(<Component onPress={onPress} />);
    fireEvent.press(getByRole('button'));
    expect(onPress).toHaveBeenCalled();
  });
});
```

### Error Handling Pattern

```python
# Custom exception hierarchy
class DomainError(Exception):
    """Base domain error"""
    pass

class ValidationError(DomainError):
    """Validation failed"""
    pass

class NotFoundError(DomainError):
    """Resource not found"""
    pass

# Test pattern
def test_raises_validation_error_on_invalid_input():
    with pytest.raises(ValidationError) as exc_info:
        service.process(invalid_data)
    assert "field is required" in str(exc_info.value)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-26 | Initial release with all 26 agents at v1.0.0 |

## Agent Inventory

| Agent | Version | Category | Framework |
|-------|---------|----------|-----------|
| async-tdd-architect | 1.0.0 | Background Jobs | Celery |
| data-tdd-architect | 1.0.0 | Data | Generic |
| devops-tdd-engineer | 1.0.0 | DevOps | Docker/K8s |
| django-data-architect | 1.0.0 | Data | Django |
| django-security-architect | 1.0.0 | Security | Django |
| django-tdd-architect | 1.0.0 | Backend | Django |
| django-vue-staging-agent | 1.0.0 | Deployment | Django+Vue |
| e2e-tdd-architect | 1.0.0 | Testing | Playwright |
| expo-deployment-agent | 1.0.0 | Deployment | Expo |
| fastapi-data-architect | 1.0.0 | Data | FastAPI |
| fastapi-security-architect | 1.0.0 | Security | FastAPI |
| fastapi-tdd-architect | 1.0.0 | Backend | FastAPI |
| fastapi-vue-staging-agent | 1.0.0 | Deployment | FastAPI+Vue |
| mobile-data-architect | 1.0.0 | Data | React Native |
| mobile-performance-optimizer | 1.0.0 | Performance | React Native |
| mobile-realtime-architect | 1.0.0 | Real-time | React Native |
| mobile-security-architect | 1.0.0 | Security | React Native |
| native-module-tdd-engineer | 1.0.0 | Native | iOS/Android |
| observability-tdd-engineer | 1.0.0 | Monitoring | OpenTelemetry |
| performance-tdd-optimizer | 1.0.0 | Performance | Django/Vue |
| project-orchestrator | 1.0.0 | Orchestration | All |
| react-native-tdd-architect | 1.0.0 | Mobile | React Native |
| realtime-tdd-architect | 1.0.0 | Real-time | WebSocket |
| security-tdd-architect | 1.0.0 | Security | Generic |
| tdd-test-specialist | 1.0.0 | Testing | All |
| vue-tdd-architect | 1.0.0 | Frontend | Vue.js |
