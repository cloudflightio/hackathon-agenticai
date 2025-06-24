# Agent Hackathon

Welcome to the **Agent Hackathon**!
This repository represents the challenge of the hackathon organized by cloudflight for the 2025 agentic AI roundtable at microsoft in munich.
The idea is to implement a customer support agent for an onlince electronics retailer. More info about the task can be found down below in "Hackathon Task and Data description".
This code is dedicated to building, testing, and showcasing this agentic approach using [OpenAI's `agents` library](https://github.com/openai/openai-agents-python) and microsoft azure.


## Setup and run

1. Clone the repository

   ```bash
   git clone git@gitlab.com:your-group/agent-hackathon.git
   cd agent-hackathon
   ```

2. Install uv as package manager
   - via pipx
      ```bash
      pipx install uv
      ```
   - OR with winget
      ```bash
      winget install --id=astral-sh.uv  -e
      ```

3. Sync the project

   ```bash
   uv sync
   ```

4. Run the app

   For a graphical interface:
   ```bash
   uv run agent_hackathon/frontend.py
   ```

   For a command line interface:
   ```bash
   uv run agent_hackathon/terminal_interface.py
   ```

5. (optional) Configure Your IDE to Use the Virtual Environment
   This is necessary for your IDE to find the imports.
   The app will also run without it, but the IDE will show warnings and you cannot open the imports from within the IDE.
   In your IDE you have to set your Python interpreter as the python version from the virtual environment.
   For VS Code this works as follows:

   * Open the Command Palette

      ```bash
      Ctrl+Shift+P
      ```

   * Select Python Interpreter from your virtual environment
   Type "Python: Select Interpreter"
   Choose the interpreter from the `.venv` directory (should show up in the list)

6. Tracing your runs
   To view detailed traces of your agentic AI runs, use MLflow (auto installed via the `uv sync` in step 2). Tracing helps you understand the execution flow, see handoffs, debug issues, and analyze performance.

   Run the following command in a new terminal:

   ```bash
   mlflow server --host 127.0.0.1 --port 5000 --no-serve-artifacts
   ```

## Environment variables

This project needs environment variables to run.
The needed variables are saved in `.env` and `.env.shared`.\
`.env.shared` only holds uncritical values, like settings or URLs.\
`.env` holds the subscription keys for used azure services, it is therefore not checked in to gitlab.\
As an example `.env.example` holds the same variables, for the actual keys ask a collegue to transfer them securely.

## Prerequisites
* python 3.12
* pipx (for installing UV)
* uv
* Git
* Azure subscription (for API access, see `.env.example`)
* An IDE

# Hackathon Task and Data description
This is a fictional electronics retailer with an online platform. On this platform, users have the opportunity to submit inquiries to a service agent.
A wide range of inquiries can occur, from product questions and technical problems to the status of active orders.
Specialized agents are used to answer these inquiries, each designed to expertly manage specific types of inquiries, ensuring customers receive knowledgeable and relevant support.

## Data (provided by us):
To enable the development of these intelligent agents, a set of mock data will be provided, simulating real-world information:

* **Product Catalog**: A comprehensive list of all products offered by the retailer. This includes essential details such as a unique id for each product, its name, the category it belongs to (e.g., "Laptops", "Audio Equipment"), current price, stock availability (e.g., in stock, out of stock, backorder), and a detailed description of its features and specifications.

* **Customers**: Information about the retailer's customer base. Each customer record will have an id, their name, crucial contact info (like email address, phone number), and potentially other relevant details such as purchase history or loyalty status (...).

* **Orders**: Data related to customer purchases. This includes the product(s) ordered, the customer who placed the order, the current status of the order (e.g., "processing," "shipped," "delivered"), the total cost, the date of purchase, a list of items in the order, and shipping tracking information where applicable.

# Codebase
This repository contains the following codebase to start the development.

### Main Conversation Loop:
This is the core engine that handles the interaction flow, managing how user Input is received and how agent Output (responses) are delivered back to the user. This is implemented two times for different interactions:
+ A GUI, implemented with chainlit in 'frontend.py'
+ A terminal interface implemented in 'terminal_interface.py'

## Basic Framework for Agents:
A skeletal structure for the different types of AI agents you'll be building. This includes placeholders or initial designs for:
+ A **Coordinator Agent**: Responsible for initially receiving all user queries and routing them to the appropriate specialized agent based on the nature of the inquiry.

+ An **Order Logistics Agent**: Specialized in handling inquiries related to the physical aspects of customer orders. This includes tracking shipments, managing returns and exchanges, addressing delivery issues, and providing information on order fulfillment processes.

+ An **Account Management and Billing Agent**: Dedicated to assisting customers with their account details and financial transactions. Responsibilities include helping users update personal information (e.g., addresses, contact details), managing saved payment methods, clarifying billing statements and invoices, processing refunds related to billing errors, and answering questions about charges or payment issues.

+ A **Product Support Agent**: Focused on providing detailed information about products, assisting with troubleshooting technical issues, and answering product-specific questions or compatibility concerns.

The agents are defined for the OpenAI Agents SDK. (https://openai.github.io/openai-agents-python/)
The agents are created in the 'agent_models.py' file.
As the prompts can be very large and thus make the code hard to read, they are defined in the 'agent_system_prompts.py' file.

**Coordinator Agent Prompt**: An initial, example prompt designed to guide the behavior of the Coordinator agent, particularly in how it analyzes incoming requests to determine user intent accurately.

## Utilities
**Examples for Tools**: Sample code illustrating how "tools" (which are essentially functions or API calls that agents can use to perform specific actions or retrieve dynamic, real-time information) can be defined and integrated into the agent framework.

**Azure AI Search Integration**: The codebase includes an implemented connection to Azure AI services. Several pre-built methods for data retrieval and performing data searches via Azure AI are provided to facilitate interaction with backend data sources.

**Logging / Error Handling**: Basic mechanisms for recording important events and system states (logging) and for gracefully managing unexpected issues or failures (error handling). Logging will be facilitated either through MLflow, which provides a graphical user interface (GUI) for tracking experiments and outputs, or via direct console output within the terminal interface. This detailed logging is especially useful for debugging and understanding the system's behavior, allowing participants to clearly see the handoffs between agents (e.g., Coordinator to Product Support) and trace the messages exchanged during an interaction.

## Tasks before Lunch

### 1. Handoffs
Handoffs in agentic AI use cases are necessary when a single AI reaches its limitations or when human judgment, expertise, or empathy is required. They ensure that complex or sensitive situations beyond the AI's current capabilities are handled appropriately. This improves the quality of the resolution and ensures user satisfaction. For now, we will only handle handoffs between the previously described specialized agents.

The task is to **Implement the handoff logic for the Coordinator agent**. This involves programming the Coordinator to accurately analyze the user's initial query (intent recognition) and determine which specialized agent (Order Logistics, Account Management & Billing, or Product Support) is best equipped to handle it. You may need to supplement its prompt or refine its logic to improve its decision-making accuracy and reduce misrouting.

Hint: What handoffs are available is defined when creating the agent. The Agent will also need to know about the handoffs in its system prompt. (https://openai.github.io/openai-agents-python/handoffs/)

**Sucess criteria**:
+ The user's intention (e.g., asking about an order shipment, needing to update payment info, requiring product help, reporting a fault) is correctly classified by the Coordinator, and the inquiry is routed via a correct handoff to the designated specialist agent. The handoff should be seamless from the user's perspective.
+ The specialist agent responds based on its programming and prompt, aiming to be helpful to the best of its knowledge and abilities within its defined scope. At this initial stage, since database integration is not yet complete, it's acceptable if the agent hallucinates or invents plausible-sounding details (e.g., a fictional order status or a generic troubleshooting step). The primary focus is on the successful handoff mechanism and basic conversational response generation; no database yet.

#### Testing Handoff
+ start the mlfow backend `mlflow server --host 127.0.0.1 --port 5000 --no-serve-artifacts`
+ start the frontend `uv run agent_hackathon/frontend.py`
+ Example questions to the coordinator: `"What is the status of my order ORD001?"`
+ Check in the mlfow webinterface in  the  "traces" tab if a handoff occurred

### 2. **Design Specialized Agent 1**
(e.g., Order Logistics Agent - to answer questions without tools). This task involves fleshing out the first of your specialized agents. "Designing" here means defining its core purpose (e.g., tracking packages, initiating returns), the specific types of questions it should be able to address (even if generically at first), and its overall conversational style and persona. It will operate without tools initially.

### 3. **Design Specialized Agent 2**
(e.g., Account Management & Billing Agent - to answer questions without tools). Similar to the first, design the second specialized agent. This agent will focus on account modifications (e.g., "I can help you update your address") and billing inquiries (e.g., "I can explain charges on your invoice"). It will operate without tools at this stage.

### 4. **Design Specialized Agent 3**
(e.g., Product Support Agent - to answer questions without tools). Design the third specialized agent, focusing on providing general product information, basic troubleshooting advice, and technical assistance. Again, it will operate without tools initially.

### 5. **Tool Implementation / Completion and Database Integration**
+ **Implement the necessary tools**. These tools are essentially functions or interfaces that allow the agents to perform specific actions or retrieve dynamic information beyond their static programming. Refer to the ToDos in the example code for guidance on what tools are anticipated (e.g., a tool to look up order status by ID, a tool to check product availability in the catalog, a tool to fetch customer contact details, a tool to update customer address in the database). Leverage the provided Azure AI methods for data retrieval and search where appropriate.

+ **Give the specialized agents access to the tools they need**

**Success criteria**:
+ The specialized agents can now successfully use the implemented tools to extract relevant and accurate data from the database or via Azure AI (e.g., fetch actual order details for a specific customer, confirm current stock levels for a product). This extracted data should then be seamlessly and coherently incorporated into their responses, making them factually accurate and genuinely informative.

+ Implement correct error handling for situations when the requested data does not exist in the database or through Azure AI (e.g., a customer asks for an order ID that isn't found, or a product SKU is invalid). In such cases, the agent should inform the user appropriately and gracefully (e.g., "I couldn't find an order with that ID. Could you please double-check it?") rather than inventing information or failing silently. No hallucination is permitted once database/Azure AI access is live; accuracy is paramount

## After Lunch
### 6. Enable Agents to Write Information to the Database
(e.g., change customer data). This task extends the agents' capabilities beyond just reading data (read-only access).
+ For now, Agents should only be able to change the Name of the customers.

### 7. Implement Escalation to a Human Support Employee
For complex, sensitive, or unresolved issues that the AI agents cannot adequately handle, or when a user explicitly requests human intervention, extend the Coordinator agent's functionality to include a smooth handoff to a human support agent. This is the escalation pathway. Define clear, logical triggers for when an escalation should occur.

**Success criteria**:
+ The escalation process can be reliably triggered under the defined conditions (e.g., by specific keywords, sentiment analysis, or repeated failure by the AI to resolve an issue).