"""
AI Agent for customer support.
Uses LangChain tool-calling when an LLM is configured; otherwise uses
deterministic tool routing so product/order data never comes from the LLM alone.
"""

from sqlalchemy.orm import Session
from typing import Any, List
from ai.tools import (
    search_products,
    get_product_by_name,
    get_product_stock,
    get_all_products,
    get_my_orders,
    get_order_status,
)
from config import settings
import logging
import json
import re

logger = logging.getLogger(__name__)


def format_tool_result(result: Any) -> str:
    if result is None:
        return "No results found."
    return json.dumps(result, indent=2, default=str)


def get_ai_response(message: str, user_id: int, db: Session) -> str:
    """Entry point used by the /ai/chat router."""
    try:
        if settings.AI_PROVIDER == "openai" and settings.OPENAI_API_KEY:
            return _langchain_agent_response(message, user_id, db, provider="openai")
        if settings.AI_PROVIDER == "gemini" and settings.GEMINI_API_KEY:
            return _langchain_agent_response(message, user_id, db, provider="gemini")
        return get_tool_routed_response(message, user_id, db)
    except Exception as e:
        logger.error(f"AI response failed: {e}")
        return get_tool_routed_response(message, user_id, db)


def get_tool_routed_response(message: str, user_id: int, db: Session) -> str:
    """
    Deterministic router that ALWAYS calls backend tools for data questions.
    Prevents hallucinated prices, stock, and order info.
    """
    text = message.lower().strip()

    # Orders
    if any(p in text for p in ["my orders", "order history", "orders have i", "what orders"]):
        orders = get_my_orders(user_id, db)
        if not orders:
            return "You haven't placed any orders yet."
        lines = [
            f"- Order #{o['order_id']}: ${o['total_amount']:.2f} — status {o['status']}, payment {o['payment_status']}"
            for o in orders
        ]
        return "Here are your orders:\n" + "\n".join(lines)

    order_id_match = re.search(r"order\s*#?\s*(\d+)", text)
    if ("status" in text and "order" in text) or order_id_match:
        if order_id_match:
            result = get_order_status(int(order_id_match.group(1)), user_id, db)
            if not result:
                return "I couldn't find that order for your account."
            items = ", ".join(
                f"{i['product_name']} x{i['quantity']}" for i in result["items"]
            )
            return (
                f"Order #{result['order_id']} is {result['status']} "
                f"(payment: {result['payment_status']}). Items: {items}. "
                f"Total: ${result['total_amount']:.2f}."
            )
        # No ID — show latest
        orders = get_my_orders(user_id, db)
        if not orders:
            return "You haven't placed any orders yet."
        latest = orders[0]
        return (
            f"Your latest order #{latest['order_id']} is {latest['status']} "
            f"(payment: {latest['payment_status']}), total ${latest['total_amount']:.2f}."
        )

    # Product list
    if any(
        p in text
        for p in [
            "what products",
            "available products",
            "list products",
            "show products",
            "products are available",
            "catalog",
        ]
    ):
        products = get_all_products(db)
        if not products:
            return "No products are available right now."
        lines = [
            f"- {p['name']}: ${p['price']:.2f} ({p['stock']} in stock)"
            for p in products
        ]
        return "Available products:\n" + "\n".join(lines)

    # Stock
    if "stock" in text:
        name = _extract_product_name(message, ["stock", "of", "for", "how", "much", "is", "available", "the", "a", "an"])
        if name:
            result = get_product_stock(name, db)
            if result:
                availability = (
                    f"{result['stock_quantity']} units in stock"
                    if result["in_stock"]
                    else "out of stock"
                )
                return f"{result['product_name']} is {availability} (price ${result['price']:.2f})."
            return f"I couldn't find a product matching '{name}'."
        products = search_products("", db) if False else get_all_products(db)
        return "Please tell me which product you want stock for."

    # Price
    if any(p in text for p in ["price", "cost", "how much"]):
        name = _extract_product_name(
            message,
            ["price", "cost", "of", "for", "how", "much", "is", "the", "a", "an", "what"],
        )
        if name:
            result = get_product_by_name(name, db)
            if result:
                return f"{result['name']} costs ${result['price']:.2f}. Stock: {result['stock']}."
            return f"I couldn't find a product matching '{name}'."

    # Generic product search
    if any(p in text for p in ["search", "find", "looking for", "do you have"]):
        # Use remaining words as query
        query = re.sub(
            r"\b(search|find|looking for|do you have|any|products?|for|me|please)\b",
            " ",
            text,
            flags=re.I,
        ).strip()
        if query:
            results = search_products(query, db)
            if results:
                lines = [
                    f"- {p['name']}: ${p['price']:.2f} ({p['stock']} in stock)"
                    for p in results
                ]
                return "Here's what I found:\n" + "\n".join(lines)
            return f"No products matched '{query}'."

    return (
        "I can help with:\n"
        "- Product prices and availability\n"
        "- Stock levels\n"
        "- Your order status\n"
        "- Order history\n\n"
        "Ask something like: \"What is the price of iPhone 15?\" or \"What is the status of my order?\""
    )


def _extract_product_name(message: str, stop_words: List[str]) -> str:
    words = re.findall(r"[A-Za-z0-9]+", message)
    filtered = [w for w in words if w.lower() not in stop_words]
    return " ".join(filtered).strip()


def _langchain_agent_response(message: str, user_id: int, db: Session, provider: str) -> str:
    """LangChain agent with tools bound to the authenticated user + DB session."""
    try:
        from langchain.agents import Tool, initialize_agent, AgentType

        if provider == "openai":
            from langchain_openai import ChatOpenAI

            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0,
                api_key=settings.OPENAI_API_KEY,
            )
        else:
            from langchain_google_genai import ChatGoogleGenerativeAI

            llm = ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                temperature=0,
                google_api_key=settings.GEMINI_API_KEY,
            )

        tools = [
            Tool(
                name="search_products",
                func=lambda q: format_tool_result(search_products(q, db)),
                description="Search active products by name/description. Input: search query string.",
            ),
            Tool(
                name="get_product_by_name",
                func=lambda name: format_tool_result(get_product_by_name(name, db)),
                description="Get product details/price by name. Input: product name.",
            ),
            Tool(
                name="get_product_stock",
                func=lambda name: format_tool_result(get_product_stock(name, db)),
                description="Get stock for a product by name. Input: product name.",
            ),
            Tool(
                name="get_all_products",
                func=lambda _: format_tool_result(get_all_products(db)),
                description="List all active products. Input: unused string.",
            ),
            Tool(
                name="get_my_orders",
                func=lambda _: format_tool_result(get_my_orders(user_id, db)),
                description="Get the authenticated customer's orders. Input: unused string. Never ask for user_id.",
            ),
            Tool(
                name="get_order_status",
                func=lambda oid: format_tool_result(get_order_status(int(str(oid).strip()), user_id, db)),
                description="Get status of an order belonging to the authenticated user. Input: order id number.",
            ),
        ]

        agent = initialize_agent(
            tools,
            llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=False,
            handle_parsing_errors=True,
            max_iterations=4,
        )

        system_hint = (
            "You are an e-commerce support assistant. "
            "ALWAYS use tools for prices, stock, products, and orders. "
            "Never invent data. Never ask for or accept another user's id. "
            f"Authenticated user_id is already bound to tools ({user_id}).\n\n"
            f"Customer question: {message}"
        )
        return str(agent.run(system_hint)).strip()
    except Exception as e:
        logger.warning(f"LangChain agent failed ({provider}): {e}; falling back to tool router")
        return get_tool_routed_response(message, user_id, db)
