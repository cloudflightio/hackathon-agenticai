import json
from typing import Any, Dict
from pydantic import BaseModel


def format_pydantic_output(output: Any, max_length: int = 200) -> str:
    """
    Format Pydantic model output for logging.

    Args:
        output: The output to format (could be Pydantic model or any type)
        max_length: Maximum length of string representation

    Returns:
        Formatted string representation
    """
    if hasattr(output, 'model_dump'):
        # It's a Pydantic model
        model_name = output.__class__.__name__

        # Special formatting for known models
        if model_name == 'SearchResult':
            return f"SearchResult(query='{output.query}', found={output.results_count} products)"

        elif model_name == 'Order':
            return (f"Order(id={output.order_id}, status={output.status}, "
                   f"total=${output.total_amount}, items={len(output.items)})")

        elif model_name == 'Customer':
            return f"Customer(id={output.customer_id}, name='{output.name}', email='{output.email}')"

        elif model_name == 'Product':
            return (f"Product(id={output.product_id}, name='{output.name}', "
                   f"price=${output.price}, stock={output.stock_count})")

        else:
            # Generic Pydantic model - show condensed dict
            try:
                data = output.model_dump()
                # Show first few key-value pairs
                preview_items = list(data.items())[:3]
                preview = ', '.join(f"{k}={repr(v)}" for k, v in preview_items)
                if len(data) > 3:
                    preview += f", ... ({len(data)} fields total)"
                return f"{model_name}({preview})"
            except:
                # Fallback to string representation
                return str(output)[:max_length] + ("..." if len(str(output)) > max_length else "")

    elif isinstance(output, list):
        # Handle lists (like List[Order])
        if output and hasattr(output[0], 'model_dump'):
            model_name = output[0].__class__.__name__
            return f"List[{model_name}] with {len(output)} items"
        else:
            return f"List with {len(output)} items"

    elif isinstance(output, dict):
        # Format dictionary
        preview_items = list(output.items())[:3]
        preview = ', '.join(f"{k}={repr(v)}" for k, v in preview_items)
        if len(output) > 3:
            preview += f", ... ({len(output)} keys total)"
        return f"Dict({preview})"

    elif isinstance(output, bool):
        return str(output)

    elif output is None:
        return "None"

    else:
        # Default string representation with truncation
        output_str = str(output)
        return output_str[:max_length] + ("..." if len(output_str) > max_length else "")


def log_intermediate_agent_results(result, cycle_counter):
    """
    Log RunResult in a clean, informative format.
    """
    print(f"\n{'='*60}")
    print(f"CYCLE {cycle_counter} RESULTS")
    print(f"{'='*60}")

    if result.new_items:
        print("\n📋 NEW ITEMS:")
        print("-" * 40)

        for i, item in enumerate(result.new_items):
            item_type = getattr(item, 'type', 'unknown')
            agent_name = getattr(getattr(item, 'agent', None), 'name', 'unknown')

            # Use emojis for different item types
            type_emoji = {
                'tool_call_item': '🔧',
                'tool_call_output_item': '📤',
                'message_output_item': '💬',
                'handoff_call_item': '🤝',
                'handoff_output_item': '✅'
            }.get(item_type, '❓')

            print(f"\n{type_emoji} Item {i}: {item_type}")
            print(f"   Agent: {agent_name}")

            # Type-specific details
            if item_type == 'tool_call_item':
                if hasattr(item, 'raw_item') and hasattr(item.raw_item, 'name'):
                    print(f"   Tool: {item.raw_item.name}")
                    if hasattr(item.raw_item, 'arguments'):
                        try:
                            args = json.loads(item.raw_item.arguments) if isinstance(item.raw_item.arguments, str) else item.raw_item.arguments
                            formatted_args = json.dumps(args, indent=6).replace('\n', '\n   ')
                            print(f"   Args: {formatted_args}")
                        except:
                            print(f"   Args: {item.raw_item.arguments}")

            elif item_type == 'tool_call_output_item':
                if hasattr(item, 'output'):
                    formatted_output = format_pydantic_output(item.output)
                    print(f"   Output: {formatted_output}")

            elif item_type == 'message_output_item':
                if hasattr(item, 'raw_item') and hasattr(item.raw_item, 'content'):
                    for content in item.raw_item.content:
                        if hasattr(content, 'text'):
                            # Show first 150 chars of message
                            text_preview = content.text[:150].replace('\n', ' ')
                            if len(content.text) > 150:
                                text_preview += "..."
                            print(f"   Message: {text_preview}")

            elif item_type in ['handoff_call_item', 'handoff_output_item']:
                source = getattr(getattr(item, 'source_agent', None), 'name', 'unknown')
                target = getattr(getattr(item, 'target_agent', None), 'name', 'unknown')
                if target != 'unknown':
                    print(f"   Handoff: {source} → {target}")

    # Token usage summary
    if result.raw_responses:
        total_tokens = sum(
            getattr(resp, 'usage', type('', (), {'total_tokens': 0})).total_tokens
            for resp in result.raw_responses
        )
        print(f"\n📊 TOKEN USAGE: {total_tokens} total tokens across {len(result.raw_responses)} responses")

    # Final output preview
    print("\n💡 FINAL OUTPUT:")
    print("-" * 40)
    if result.final_output:
        # Show first 300 chars of final output
        output_preview = result.final_output[:300].strip()
        if len(result.final_output) > 300:
            output_preview += "..."
        print(output_preview)
    else:
        print("(No final output)")

    print(f"\n{'='*60}\n")