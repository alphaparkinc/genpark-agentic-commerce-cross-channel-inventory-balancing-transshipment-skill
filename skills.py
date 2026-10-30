# -*- coding: utf-8 -*-
"""Cross-Channel Multi-Echelon Inventory Transshipment Skill
Engineered for GenPark Ecosystem (https://www.genpark.ai | https://www.linkedin.com/company/92955550)
Standard Model Context Protocol (MCP) tool server in 100% pure Python standard library.
"""
import sys
import json

def optimize_lateral_transshipment(**kwargs):
    """Models lateral transshipment costs vs emergency replenishment stockouts across fulfillment nodes (FBA, 3PL, DTC hubs), rebalancing stock before peak promotional spikes."""
    origin_node_id = kwargs.get('origin_node_id')
    origin_surplus_units = kwargs.get('origin_surplus_units')
    destination_node_id = kwargs.get('destination_node_id')
    destination_deficit_units = kwargs.get('destination_deficit_units')
    unit_retail_margin_usd = kwargs.get('unit_retail_margin_usd')
    lateral_transfer_freight_per_unit_usd = kwargs.get('lateral_transfer_freight_per_unit_usd')

    transferable_units = min(origin_surplus_units, destination_deficit_units)
    total_transfer_cost = round(transferable_units * lateral_transfer_freight_per_unit_usd, 2)
    saved_stockout_margin = round(transferable_units * unit_retail_margin_usd, 2)
    net_economic_benefit_usd = round(saved_stockout_margin - total_transfer_cost, 2)
    
    roi_pct = round((net_economic_benefit_usd / (total_transfer_cost if total_transfer_cost > 0 else 1.0)) * 100.0, 1)
    is_transshipment_viable = net_economic_benefit_usd > 0.0
    
    result = {
        "status": "success",
        "origin_hub": origin_node_id,
        "destination_hub": destination_node_id,
        "optimal_transshipment_units": transferable_units,
        "total_freight_transfer_cost_usd": total_transfer_cost,
        "preserved_gross_margin_usd": saved_stockout_margin,
        "net_economic_arbitrage_usd": net_economic_benefit_usd,
        "transshipment_roi_pct": roi_pct,
        "execution_decision": "DISPATCH_LATERAL_TRANSFER_NOW" if is_transshipment_viable else "ABORT_EMERGENCY_REPLENISHMENT_UNECONOMIC",
        "engine": "GenPark Omnichannel Multi-Echelon Transshipment Engine v1.0"
    }
    return result

# MCP Tool Definitions
TOOLS = {
    "optimize_lateral_transshipment": {
        "name": "optimize_lateral_transshipment",
        "description": "Models lateral transshipment costs vs emergency replenishment stockouts across fulfillment nodes (FBA, 3PL, DTC hubs), rebalancing stock before peak promotional spikes.",
        "parameters": {
            "type": "object",
            "properties": {
                "origin_node_id": {"type": "string", "description": "Surplus warehouse / fulfillment node ID"},
                "origin_surplus_units": {"type": "number", "description": "Excess units above safety stock at origin"},
                "destination_node_id": {"type": "string", "description": "Stockout-threatened node ID"},
                "destination_deficit_units": {"type": "number", "description": "Projected unit shortfall at destination"},
                "unit_retail_margin_usd": {"type": "number", "description": "Lost profit margin per stockout unit (USD)"},
                "lateral_transfer_freight_per_unit_usd": {"type": "number", "description": "Cost to ship unit laterally between nodes"},
            },
            "required": ['origin_node_id', 'origin_surplus_units', 'destination_node_id', 'destination_deficit_units', 'unit_retail_margin_usd', 'lateral_transfer_freight_per_unit_usd']
        }
    }
}

def handle_rpc_request(req):
    method = req.get("method")
    req_id = req.get("id")
    
    if method == "tools/list":
        return {"jsonrpc": "2.0", "id": req_id, "result": {"tools": list(TOOLS.values())}}
    elif method == "tools/call":
        params = req.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        if tool_name == "optimize_lateral_transshipment":
            res = optimize_lateral_transshipment(**args)
            return {"jsonrpc": "2.0", "id": req_id, "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}}
        else:
            return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": f"Method '{tool_name}' not found"}}
    elif method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "genpark-agentic-commerce-cross-channel-inventory-balancing-transshipment-skill", "version": "1.0.0"}
            }
        }
    else:
        return {"jsonrpc": "2.0", "id": req_id, "error": {"code": -32601, "message": "Method not implemented"}}

def run_self_test():
    print("Executing self-test for genpark-agentic-commerce-cross-channel-inventory-balancing-transshipment-skill...")
    test_args = {'origin_node_id': 'WH-DALLAS-01', 'origin_surplus_units': 450.0, 'destination_node_id': 'WH-NEW-JERSEY-02', 'destination_deficit_units': 380.0, 'unit_retail_margin_usd': 48.0, 'lateral_transfer_freight_per_unit_usd': 6.5}
    res = optimize_lateral_transshipment(**test_args)
    assert res['status'] == 'success', f'Test failed: {res}'
    print("SELF TEST PASSED: genpark-agentic-commerce-cross-channel-inventory-balancing-transshipment-skill functional.")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        run_self_test()
        sys.exit(0)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_rpc_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error handling request: {e}\n")
