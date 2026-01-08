# UI Implementation

**Version:** 1.0

---

## Chainlit UI

### Key Features
- Chat-based interaction
- Session management
- Business plan versioning
- Two-column analysis display
- Debug panel (developer mode)

### Main Flow
```python
@cl.on_chat_start
async def start():
    """Initialize session"""

@cl.on_message
async def main(message: cl.Message):
    """Handle user messages"""
    
async def run_analysis(context):
    """Run and display analysis"""
```

### Running
```bash
chainlit run src/vira/ui/chainlit_app.py --port 8000
```

---

**See:** `../02-ARCHITECTURE/06-Frontend-Architecture.md` for details
