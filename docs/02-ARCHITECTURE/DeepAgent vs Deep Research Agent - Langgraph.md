## **1\. Repository 1: deep\_research\_from\_scratch \- Architecture Analysis**

**Core Design Pattern**: Multi-phase workflow architecture

* Three-phase process: Scope → Research → Write  
* Uses LangGraph's StateGraph for workflow orchestration  
* Supervisor-Worker pattern for multi-agent coordination

**Key Components**:

1. **Scoping Phase**: User clarification \+ brief generation with structured output (Pydantic)  
2. **Research Phase**:  
   * Supervisor agent delegates to worker agents  
   * Workers use ReAct loops for tool calling  
   * Parallel execution via asyncio.gather()  
3. **Writing Phase**: Report synthesis from gathered context

**State Management**:

* Complex state flows across subgraphs  
* LangGraph Commands for flow control  
* Structured output schemas (ClarifyWithUser, ResearchQuestion, ConductResearch, ResearchComplete)

**Tool Integration**:

* Tavily for web search  
* MCP (Model Context Protocol) servers  
* Content summarization to compress results

**Memory/Context**:

* Chat history compression into research brief  
* Sub-agent findings pruning before returning to supervisor  
* Context engineering to prevent window overflow

**Error Handling**:

* Conditional routing based on clarification needs  
* Supervisor reflection on whether findings sufficiently address brief

## **2\. Repository 2: deep-agents-from-scratch \- Architecture Analysis**

**Core Design Pattern**: Context engineering with single-agent \+ delegation

* Inspired by Claude Code, Manus patterns  
* Focus on long-horizon task execution (\~50 tool calls)  
* Middleware architecture for composability

**Key Components**:

1. **TODO Planning Tool**: Task tracking with status (pending/in\_progress/completed) \- essentially a no-op for context engineering  
2. **File System Backend**: Virtual file system (ls, read\_file, write\_file, edit\_file)  
3. **Sub-agent Delegation**: Context isolation via task() tool  
4. **ReAct Loop Foundation**: create\_agent component

**State Management**:

* Agent state includes TODO lists, file system, sub-agent registry  
* Information persistence through files  
* Context offloading to reduce token usage

**Tool Integration**:

* Built-in tools: write\_todos(), task()  
* File operations for memory  
* Custom tools via middleware

**Memory/Context**:

* File system as "memory" across conversation turns  
* Context offloading \- store detailed info in files  
* Automatic summarization when context \> 170K tokens  
* Large tool results (\>20K tokens) auto-saved to files

**Error Handling**:

* Task status tracking prevents drift  
* Sub-agent isolation contains failures  
* Progress monitoring via TODO list

## **3\. Essential Similarities**

1. **LangGraph Foundation**: Both built on LangGraph for orchestration  
2. **ReAct Core**: Both use ReAct (Reason-Act) loops as the foundation  
3. **Sub-agent Delegation**: Both support delegating to specialized agents  
4. **Context Engineering Priority**: Both heavily focus on managing context windows  
5. **Tool Calling**: Both use structured tool calling  
6. **Pydantic Schemas**: Both use structured output for reliability  
7. **Research Focus**: Both designed for complex research/long-horizon tasks

## **4\. Key Differences**

**A. Orchestration Model**:

* Repo 1: Explicit supervisor-worker hierarchy with centralized coordination  
* Repo 2: Single-agent with optional delegation, more autonomous

**B. Context Management**:

* Repo 1: Brief compression, result pruning, subgraph isolation  
* Repo 2: File system backend, TODO lists, automatic context offloading

**C. State Persistence**:

* Repo 1: State flows through subgraphs, transient per-research  
* Repo 2: Virtual file system persists across interactions

**D. Planning Approach**:

* Repo 1: Scoping phase upfront, supervisor manages decomposition  
* Repo 2: TODO tool for continuous planning, agent self-manages

**E. Modularity**:

* Repo 1: Notebook-based progression, subgraph composition  
* Repo 2: Middleware architecture, composable components

**F. Tool Patterns**:

* Repo 1: External tools (Tavily, MCP servers)  
* Repo 2: Built-in infrastructure tools \+ custom tools

## **5\. Real-World Implications**

**Scalability**:

* Repo 1: Parallel sub-agents via asyncio.gather() \- good for parallelizable research  
* Repo 2: Sub-agent delegation \+ file system \- better for long sequential tasks

**Evaluability**:

* Repo 1: Clearer phases make evaluation easier (scope quality, research completeness, report quality)  
* Repo 2: TODO tracking provides progress visibility, but more emergent behavior

**Maintainability**:

* Repo 1: More complex state management, subgraph composition  
* Repo 2: Middleware pattern is more modular and extensible

**Reliability**:

* Repo 1: Supervisor reflection provides quality control  
* Repo 2: File system prevents context overflow, TODO prevents drift \</scratchpad\>

---

# **Comprehensive Architectural Comparison: deep\_research\_from\_scratch vs deep-agents-from-scratch**

## **Executive Summary**

These two LangChain repositories represent fundamentally different paradigms for building sophisticated AI agents. **deep\_research\_from\_scratch** implements a structured, multi-phase workflow architecture with explicit supervisor-worker coordination, optimized for parallelizable research tasks. **deep-agents-from-scratch** implements a context engineering approach with a single autonomous agent enhanced by planning tools, file systems, and sub-agent delegation, optimized for long-horizon sequential tasks. Both are built on LangGraph, but their design philosophies target different problem spaces.

---

## **1\. Essential Similarities**

Both repositories share fundamental design principles that reflect current best practices in agentic system design.

### **LangGraph as the Orchestration Foundation**

Both repositories leverage LangGraph's `StateGraph` for workflow orchestration, representing a clear industry move away from deprecated `create_react_agent` patterns toward deterministic, graph-based architectures. 

This choice provides checkpointing, resumable workflows, and explicit state management that ReAct-style loops cannot offer.

### **ReAct-Style Tool Calling Core**

At their foundation, both systems implement the Reason-Act pattern where an LLM decision node alternates with a tool execution node. 

However, they wrap this pattern differently—the first repository uses it within worker agents coordinated by a supervisor, while the second uses it as the primary loop enhanced with context engineering tools.

### **Structured Output for Reliability**

Both repositories extensively use Pydantic schemas to constrain LLM outputs. This prevents hallucination and ensures reliable decision-making:

python  
*\# deep\_research\_from\_scratch approach*  
class ClarifyWithUser(BaseModel):  
    needs\_clarification: bool  
    clarification\_question: Optional\[str\]

class ResearchQuestion(BaseModel):  
    topic: str  
    sub\_questions: List\[str\]  
      
*\# deep-agents-from-scratch approach*    
class TodoItem(BaseModel):  
    task: str  
    status: Literal\["pending", "in\_progress", "completed"\]  
\`\`\`

#### **Context Engineering as a First-Class Concern**

Both repositories recognize that naive context accumulation causes context window overflow and quality degradation. They implement compression and pruning strategies, though through different mechanisms (brief compression vs. file offloading).

#### **Sub-Agent Delegation for Context Isolation**

Both support spawning specialized sub\-agents to handle focused subtasks with isolated context windows. This prevents the main agent's context from becoming polluted with irrelevant details and enables parallel or delegated work.

\---

*\#\# 2\. Key Architectural Differences*

*\#\#\# Difference A: Orchestration Model — Supervisor Hierarchy vs. Autonomous Agent*

\*\*deep\_research\_from\_scratch\*\* implements an explicit \*\*supervisor\-worker hierarchy\*\*:  
\`\`\`  
┌─────────────────────────────────────────────────────────────┐  
│                    SUPERVISOR PATTERN                       │  
├─────────────────────────────────────────────────────────────┤  
│                                                             │  
│    ┌──────────┐                                             │  
│    │Supervisor│ ←── Decides what research is needed         │  
│    └────┬─────┘                                             │  
│         │                                                   │  
│    ┌────┴────────┬────────────┐                            │  
│    ↓             ↓            ↓                            │  
│ ┌────────┐  ┌────────┐  ┌────────┐                         │  
│ │Worker 1│  │Worker 2│  │Worker 3│  ←── Execute research   │  
│ └────────┘  └────────┘  └────────┘                         │  
│         │             │           │                         │  
│         └──────┬──────┴───────────┘                        │  
│                ↓                                            │  
│         \[Cleaned findings returned to supervisor\]          │  
│                                                             │  
└─────────────────────────────────────────────────────────────┘  
\`\`\`

The supervisor has a single job: delegate research tasks to an appropriate number of sub\-agents, wait for results, and determine if more research is needed. Workers don't communicate with each other—all coordination flows through the supervisor.

\*\*deep\-agents\-from\-scratch\*\* implements an \*\*autonomous single\-agent with optional delegation\*\*:  
\`\`\`  
┌─────────────────────────────────────────────────────────────┐  
│                 AUTONOMOUS AGENT PATTERN                    │  
├─────────────────────────────────────────────────────────────┤  
│                                                             │  
│    ┌──────────────────────────────────────┐                │  
│    │          Main Agent Loop             │                │  
│    │  ┌─────────────────────────────────┐ │                │  
│    │  │ TODO Planning Tool              │ │ ←── Self\-plans │  
│    │  ├─────────────────────────────────┤ │                │  
│    │  │ File System                     │ │ ←── Persists   │  
│    │  ├─────────────────────────────────┤ │                │  
│    │  │ task() Delegation Tool          │ │ ←── Delegates  │  
│    │  ├─────────────────────────────────┤ │                │  
│    │  │ External Tools (search, etc.)   │ │                │  
│    │  └─────────────────────────────────┘ │                │  
│    └──────────────────────────────────────┘                │  
│         │                                                   │  
│         ↓ (when task() called)                             │  
│    ┌──────────┐                                            │  
│    │ Sub\-agent│ ←── Isolated context, returns summary      │  
│    └──────────┘                                            │  
│                                                             │  
└─────────────────────────────────────────────────────────────┘  
\`\`\`

The main agent autonomously decides when to plan, when to delegate, and when to use the file system—there's no explicit orchestrator telling it what to do.

*\#\#\# Difference B: Context Management Strategy*

\*\*deep\_research\_from\_scratch\*\* uses \*\*brief compression and result pruning\*\*:

1\. The scoping phase compresses the entire user conversation into a focused research brief  
2\. Sub\-agents prune their findings before returning to the supervisor  
3\. Context is managed at workflow boundaries between subgraphs  
\`\`\`  
\[User conversation\] → Compression → \[Research Brief\]  
                                           ↓  
                            \[Sub\-agent raw findings\]  
                                           ↓  
                            Pruning/Cleaning  
                                           ↓  
                            \[Cleaned findings to supervisor\]  
\`\`\`

\*\*deep\-agents\-from\-scratch\*\* uses \*\*file system offloading and automatic summarization\*\*:

1\. Large tool results (\>20K tokens) automatically saved to files  
2\. Agent can write notes, intermediate results to files  
3\. Automatic conversation summarization when context exceeds 170K tokens  
4\. Files act as shared workspace across all agents  
\`\`\`  
\[Large tool result\] → Auto\-save to file → \[File reference in context\]  
                                                    ↓  
\[Agent reads file when needed\] ←────────────────────┘

\[Context \> 170K tokens\] → Summarize older messages → \[Compressed context\]

### **Difference C: Planning Architecture**

**deep\_research\_from\_scratch** implements **upfront scoping with supervisor decomposition**:

The workflow explicitly starts with a scoping phase that transforms user input into a structured research brief. The supervisor then decomposes this brief into sub-topics for parallel execution:

python  
*\# Phase 1: Scope (clarify → brief generation)*  
*\# Phase 2: Research (supervisor → workers)*

*\# Phase 3: Write (synthesis)*

**deep-agents-from-scratch** implements **continuous self-planning via TODO tool**:

The agent maintains a TODO list throughout execution, updating it as new information emerges. Interestingly, the TODO tool is essentially a "no-op"—it doesn't execute anything, but forces the agent to articulate its plan:

python  
*\# The write\_todos() tool forces planning recitation*  
todos \= \[  
    {"task": "Search for X", "status": "pending"},  
    {"task": "Analyze findings", "status": "pending"},  
    {"task": "Write summary", "status": "pending"}  
\]

*\# Agent updates status as it progresses*

todos\[0\]\["status"\] \= "completed"  *\# After search*

This pattern, inspired by Claude Code, keeps the agent "on track" during long-horizon tasks by forcing explicit planning articulation.

### **Difference D: State Persistence Model**

**deep\_research\_from\_scratch** uses **transient state with subgraph composition**:

State flows through the workflow via LangGraph's state management, but is primarily transient—designed for a single research session. State includes:

* Messages/conversation history  
* Current research brief  
* Accumulated findings from workers

**deep-agents-from-scratch** uses **persistent file system state**:

The virtual file system persists across conversation turns, enabling true "memory":

python  
*\# State includes persistent storage*  
class AgentState(TypedDict):  
    messages: Annotated\[list, add\_messages\]  
    todos: List\[TodoItem\]  

    files: Dict\[str, str\]  *\# Virtual file system*

### **Difference E: Modularity Architecture**

**deep\_research\_from\_scratch** uses **subgraph composition**:

The system is built from composable subgraphs (scoping subgraph, researcher subgraph, writer subgraph) connected via the main workflow:

python  
*\# Subgraph composition pattern*  
main\_graph \= StateGraph(OverallState)  
main\_graph.add\_node("scope", scoping\_subgraph)  
main\_graph.add\_node("research", supervisor\_subgraph)

main\_graph.add\_node("write", writer\_node)

**deep-agents-from-scratch** uses **middleware composition**:

Capabilities are added via stackable middleware:

python  
*\# Middleware composition pattern*  
agent \= create\_deep\_agent(  
    middleware\=\[  
        TodoListMiddleware(),      *\# Planning capability*  
        FilesystemMiddleware(),    *\# File system capability*  
        SubAgentMiddleware(),      *\# Delegation capability*  
        CustomToolMiddleware(\[my\_tools\])  *\# Custom tools*  
    \]

)

This middleware pattern (inspired by web frameworks) makes it trivial to add or remove capabilities without touching core agent logic.

---

## **3\. Real-World Implications**

### **Scalability Considerations**

**deep\_research\_from\_scratch** excels at **parallelizable research**:

The supervisor pattern with `asyncio.gather()` enables true concurrent execution of independent research topics. When a research brief can be decomposed into independent sub-topics, multiple workers investigate simultaneously:

python  
*\# Parallel execution in supervisor*  
async def execute\_parallel\_research(topics: List\[str\]):  
    tasks \= \[research\_agent.ainvoke(topic) for topic in topics\]  
    results \= await asyncio.gather(\*tasks)  
    return results  
\`\`\`

\*\*Trade\-off\*\*: The supervisor becomes a bottleneck for task distribution and result aggregation. Complex research with many interdependent topics may not parallelize well.

\*\*deep\-agents\-from\-scratch\*\* excels at \*\*long sequential workflows\*\*:

The file system and TODO patterns scale well for tasks requiring 50\+ tool calls (like Manus\-style agents). Context offloading prevents the token explosion that would otherwise make such long workflows impossible:

\*\*Trade\-off\*\*: Sequential execution means longer wall\-clock time. However, for tasks where each step depends on previous results, this is actually appropriate.

*\#\#\# Evaluability and Testing*

\*\*deep\_research\_from\_scratch\*\* offers \*\*clearer evaluation boundaries\*\*:

The three\-phase architecture creates natural evaluation points:

1\. \*\*Scope Quality\*\*: Does the brief accurately capture user intent?  
2\. \*\*Research Completeness\*\*: Did workers find relevant, comprehensive information?  
3\. \*\*Report Quality\*\*: Is the final output well\-synthesized?

Each phase can be evaluated independently with targeted metrics.

\*\*deep\-agents\-from\-scratch\*\* offers \*\*progress visibility but emergent behavior\*\*:

The TODO list provides excellent progress tracking—you can see exactly what the agent planned and what's completed. However, the agent's behavior is more emergent and harder to predict:  
\`\`\`  
✓ Search for climate change impacts  
✓ Analyze scientific consensus    
→ Summarize key findings (in progress)  
○ Write final report (pending)  
\`\`\`

\*\*Trade\-off\*\*: More flexibility means harder to test comprehensively. Unit testing individual middleware is straightforward, but end\-to\-end behavior depends on agent decisions.

*\#\#\# Maintainability*

\*\*deep\_research\_from\_scratch\*\* requires \*\*understanding complex state flows\*\*:

Debugging requires understanding how state transforms across subgraphs. The LangGraph visual tools help, but the cognitive overhead is higher:  
\`\`\`  
State at scope entry → transforms → State at scope exit  
                                            ↓

                                    State at research entry → ...

**deep-agents-from-scratch** benefits from **modular middleware isolation**:

Each middleware is self-contained. To modify planning behavior, you only touch `TodoListMiddleware`. To change file handling, you only touch `FilesystemMiddleware`:

python  
*\# Easy to swap or extend individual capabilities*  
class CustomPlanningMiddleware(AgentMiddleware):  
    tools \= \[enhanced\_todo\_tool\]  
      
agent \= create\_deep\_agent(middleware\=\[  
    CustomPlanningMiddleware(),  *\# Replace default planning*  
    FilesystemMiddleware(),  
    SubAgentMiddleware()

\])

### **Reliability and Error Handling**

**deep\_research\_from\_scratch** provides **supervisor reflection for quality control**:

The supervisor explicitly reflects on whether worker findings sufficiently address the research brief. If gaps exist, it can spawn additional workers:

python  
*\# Supervisor reflection loop*  
if not findings\_address\_brief(brief, worker\_results):

    spawn\_additional\_workers(identified\_gaps)

**deep-agents-from-scratch** provides **drift prevention via TODO tracking**:

The TODO list acts as a "north star" preventing the agent from getting lost during long tasks. Status tracking ensures tasks don't get forgotten:

python  
*\# Progress monitoring prevents drift*  
for todo in todos:  
    if todo.status \== "pending" and time\_since\_update \> threshold:

        prompt\_agent\_to\_address(todo)

---

## **4\. Recommendations: When to Use Each Approach**

### **Use deep\_research\_from\_scratch When:**

**Your task naturally decomposes into parallel independent subtasks**. If you're building a research system where "Compare X vs Y vs Z" can be investigated simultaneously by separate agents, the supervisor pattern's parallel execution provides significant speed benefits.

**You need explicit quality control checkpoints**. The supervisor reflection loop ensures research completeness before proceeding. This is valuable for high-stakes research where missing important aspects is costly.

**You're building a focused research product**. The three-phase architecture (Scope → Research → Write) is specifically optimized for the research use case with clear deliverables.

**You want to integrate MCP servers**. The repository explicitly covers MCP integration, making it easier to connect external data sources.

### **Use deep-agents-from-scratch When:**

**Your task requires 20+ sequential tool calls**. The context offloading to files and automatic summarization prevent context window overflow that would break simpler architectures. If you're building something like Claude Code that handles complex multi-step coding tasks, this is the pattern.

**You need persistent memory across sessions**. The file system backend enables agents to "remember" information across conversations, which the supervisor pattern doesn't provide out of the box.

**You want maximum flexibility and extensibility**. The middleware architecture makes it trivial to add new capabilities without touching core logic. If you're building a platform that needs to support many different agent configurations, this is more maintainable.

**Your task is inherently sequential with dependencies**. When each step depends on previous results (like iterative debugging or multi-step analysis), the single-agent with planning approach is more natural than forced parallelization.

**You want to follow patterns from production systems**. This approach is explicitly modeled on Claude Code and Manus, which have proven effective for general-purpose long-horizon tasks.

### **Hybrid Approach**

For complex systems, consider combining elements of both:

python  
*\# Use supervisor pattern for parallel research phases*  
*\# with file-system-backed workers for context management*  
supervisor \= create\_supervisor\_agent(  
    workers\=\[  
        create\_deep\_agent(  *\# Each worker is a deep agent*  
            middleware\=\[FilesystemMiddleware(), TodoListMiddleware()\]  
        )  
        for \_ in range(3)  
    \]

)

This would give you the parallel coordination of the supervisor pattern with the context management robustness of the deep agents pattern.

---

## **Summary Comparison Table**

| Aspect | deep\_research\_from\_scratch | deep-agents-from-scratch |
| ----- | ----- | ----- |
| **Primary Pattern** | Supervisor-Worker Hierarchy | Autonomous Agent \+ Delegation |
| **Orchestration** | Explicit multi-phase workflow | Single agent with middleware |
| **Planning** | Upfront scoping phase | Continuous TODO tool |
| **Context Management** | Brief compression, result pruning | File system offloading |
| **Parallelization** | Native via asyncio.gather() | Sequential by default |
| **State Persistence** | Transient per-session | Persistent file system |
| **Modularity** | Subgraph composition | Middleware composition |
| **Best For** | Parallelizable research tasks | Long-horizon sequential tasks |
| **Inspired By** | Anthropic multi-agent research | Claude Code, Manus |
| **Evaluation** | Clear phase boundaries | TODO progress tracking |
| **Tool Integration** | MCP servers, Tavily | Built-in \+ custom middleware |

Both repositories represent sophisticated, production-ready approaches to building agentic systems. Your choice should be driven by the specific characteristics of your use case—particularly whether your tasks are parallelizable or sequential, and whether you need persistent memory across sessions.

