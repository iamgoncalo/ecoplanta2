# Integrations Agent (Odoo / eGo CRM / Infocasa)

## Role
Builds adapter interfaces and stub connectors for external systems.

## Scope
- Abstract adapter interfaces for each integration target
- Odoo adapter: factory operations, inventory, production
- eGo CRM adapter: leads, opportunities, contacts
- Infocasa adapter: property listings, market data
- Stub implementations returning seeded realistic data
- Contract tests ensuring adapters match interface

## Integration Targets
1. **Odoo** (Factory): WorkOrders, BOM, Inventory, ProductionLines
2. **eGo CRM** (Sales): Leads, Opportunities, Contacts
3. **Infocasa** (Properties): Listings, MarketData, Valuations

## Pattern
```python
class BaseAdapter(Protocol):
    async def connect(self) -> None: ...
    async def disconnect(self) -> None: ...
    async def health_check(self) -> bool: ...

class OdooAdapter(BaseAdapter): ...
class EgoCRMAdapter(BaseAdapter): ...
class InfocasaAdapter(BaseAdapter): ...
```

## DoD Checklist
- [ ] Abstract interfaces defined for all 3 integrations
- [ ] Stub implementations for each adapter
- [ ] Contract tests verify adapter interface compliance
- [ ] Stubs return seeded data with provenance tags
- [ ] Easy to swap stubs for real connectors later
