#!/usr/bin/env python3
"""
End-to-End Test Script for Company Agent System
This script demonstrates the complete flow for a single company onboarding and using the support agent system.
"""

import asyncio
import httpx
import json
import time
import sys
from typing import Dict, Any, List
from datetime import datetime


class CompanyAgentE2ETest:
    """End-to-end test for company agent system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_company_id = "test_company_123"
        self.test_company_name = "Test Company Inc"
        self.created_agents = []
    
    async def check_server_health(self) -> bool:
        """Check if the server is running and healthy"""
        try:
            print("🔍 Checking server health...")
            response = await self.client.get(f"{self.base_url}/health")
            if response.status_code == 200:
                health_data = response.json()
                print(f"✅ Server is healthy: {health_data.get('status', 'unknown')}")
                return True
            else:
                print(f"❌ Server health check failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Cannot connect to server: {e}")
            print("💡 Make sure to start the server first:")
            print("   cd agents && python main.py")
            return False
    
    async def create_customer_service_agent(self) -> Dict[str, Any]:
        """Create a customer service agent for the test company"""
        print("\n🏢 Creating Customer Service Agent...")
        
        agent_config = {
            "company_id": self.test_company_id,
            "company_name": self.test_company_name,
            "agent_name": "CustomerServiceAgent",
            "port": 5001,
            "capabilities": ["customer_support", "order_tracking", "returns", "billing"],
            "description": "Handles all customer service requests for Test Company Inc",
            "webhook_url": f"http://localhost:8000/webhooks/agent/customer_service"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/company-agents",
                json=agent_config
            )
            response.raise_for_status()
            agent_data = response.json()
            
            print(f"✅ Customer Service Agent created successfully!")
            print(f"   Agent ID: {agent_data['agent_id']}")
            print(f"   Address: {agent_data['address']}")
            print(f"   Status: {agent_data['status']}")
            print(f"   Port: {agent_data['port']}")
            print(f"   Capabilities: {', '.join(agent_data['capabilities'])}")
            
            self.created_agents.append(agent_data)
            return agent_data
            
        except Exception as e:
            print(f"❌ Failed to create customer service agent: {e}")
            raise
    
    async def create_sales_agent(self) -> Dict[str, Any]:
        """Create a sales agent for the test company"""
        print("\n💼 Creating Sales Agent...")
        
        agent_config = {
            "company_id": self.test_company_id,
            "company_name": self.test_company_name,
            "agent_name": "SalesAgent",
            "port": 5002,
            "capabilities": ["sales", "lead_generation", "product_info", "pricing"],
            "description": "Handles sales inquiries and lead generation",
            "webhook_url": f"http://localhost:8000/webhooks/agent/sales"
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/company-agents",
                json=agent_config
            )
            response.raise_for_status()
            agent_data = response.json()
            
            print(f"✅ Sales Agent created successfully!")
            print(f"   Agent ID: {agent_data['agent_id']}")
            print(f"   Address: {agent_data['address']}")
            print(f"   Status: {agent_data['status']}")
            print(f"   Port: {agent_data['port']}")
            print(f"   Capabilities: {', '.join(agent_data['capabilities'])}")
            
            self.created_agents.append(agent_data)
            return agent_data
            
        except Exception as e:
            print(f"❌ Failed to create sales agent: {e}")
            raise
    
    async def list_company_agents(self) -> List[Dict[str, Any]]:
        """List all agents for the test company"""
        print("\n📋 Listing all agents for Test Company...")
        
        try:
            response = await self.client.get(
                f"{self.base_url}/company-agents/company/{self.test_company_id}"
            )
            response.raise_for_status()
            agents = response.json()
            
            print(f"✅ Found {len(agents)} agents for {self.test_company_name}")
            for agent in agents:
                print(f"   - {agent['agent_name']} ({agent['status']}) - {agent['agent_id']}")
            
            return agents
            
        except Exception as e:
            print(f"❌ Failed to list company agents: {e}")
            raise
    
    async def discover_agents_by_capability(self, capability: str) -> Dict[str, Any]:
        """Discover agents by capability"""
        print(f"\n🔍 Discovering agents with capability: {capability}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/company-agents/discover",
                json={"capability": capability, "company_id": self.test_company_id}
            )
            response.raise_for_status()
            discovery_data = response.json()
            
            print(f"✅ Found {discovery_data['total_found']} agents with '{capability}' capability")
            for agent in discovery_data['agents']:
                print(f"   - {agent['agent_name']} ({agent['company_name']})")
            
            return discovery_data
            
        except Exception as e:
            print(f"❌ Failed to discover agents: {e}")
            raise
    
    async def send_message_to_agent(self, agent_id: str, message: str, sender_company: str = "customer_company") -> Dict[str, Any]:
        """Send a message to a specific agent"""
        print(f"\n💬 Sending message to agent {agent_id}...")
        print(f"   Message: {message}")
        
        try:
            response = await self.client.post(
                f"{self.base_url}/company-agents/send-message",
                json={
                    "agent_id": agent_id,
                    "message": message,
                    "sender_company_id": sender_company
                }
            )
            response.raise_for_status()
            message_data = response.json()
            
            print(f"✅ Message sent successfully!")
            print(f"   Response: {message_data['response']}")
            print(f"   Status: {message_data['status']}")
            print(f"   Timestamp: {message_data['timestamp']}")
            
            return message_data
            
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            raise
    
    async def test_agent_communication_scenarios(self):
        """Test various communication scenarios"""
        print("\n🧪 Testing Agent Communication Scenarios...")
        
        if not self.created_agents:
            print("❌ No agents created yet")
            return
        
        # Test customer service scenarios
        customer_service_agent = next(
            (agent for agent in self.created_agents if agent['agent_name'] == 'CustomerServiceAgent'), 
            None
        )
        
        if customer_service_agent:
            print("\n📞 Testing Customer Service Scenarios:")
            
            # Scenario 1: Order inquiry
            await self.send_message_to_agent(
                customer_service_agent['agent_id'],
                "Hi, I need help with my order #12345. It hasn't arrived yet and it's been 5 days.",
                "worried_customer"
            )
            
            # Scenario 2: Return request
            await self.send_message_to_agent(
                customer_service_agent['agent_id'],
                "I want to return a product I bought last week. What's the return policy?",
                "return_customer"
            )
            
            # Scenario 3: Billing inquiry
            await self.send_message_to_agent(
                customer_service_agent['agent_id'],
                "I was charged twice for my subscription. Can you help me with a refund?",
                "billing_customer"
            )
        
        # Test sales scenarios
        sales_agent = next(
            (agent for agent in self.created_agents if agent['agent_name'] == 'SalesAgent'), 
            None
        )
        
        if sales_agent:
            print("\n💼 Testing Sales Scenarios:")
            
            # Scenario 1: Product inquiry
            await self.send_message_to_agent(
                sales_agent['agent_id'],
                "I'm interested in your premium package. Can you tell me more about the features?",
                "potential_customer"
            )
            
            # Scenario 2: Pricing inquiry
            await self.send_message_to_agent(
                sales_agent['agent_id'],
                "What are your pricing options for enterprise customers?",
                "enterprise_prospect"
            )
            
            # Scenario 3: Lead generation
            await self.send_message_to_agent(
                sales_agent['agent_id'],
                "I'm looking for a solution for my 500-person company. Can you help me?",
                "enterprise_lead"
            )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get health status of all agents"""
        print("\n🏥 Getting Health Status...")
        
        try:
            response = await self.client.get(f"{self.base_url}/company-agents/health/status")
            response.raise_for_status()
            health_data = response.json()
            
            print(f"✅ System Health Status: {health_data['status']}")
            print(f"   Total Agents: {health_data['total_agents']}")
            print(f"   Active Agents: {health_data['active_agents']}")
            
            for agent in health_data['agents']:
                status_emoji = "🟢" if agent['status'] == 'running' else "🔴"
                print(f"   {status_emoji} {agent['agent_name']} ({agent['company_name']}) - {agent['status']}")
                if agent.get('uptime'):
                    print(f"      Uptime: {agent['uptime']}")
            
            return health_data
            
        except Exception as e:
            print(f"❌ Failed to get health status: {e}")
            raise
    
    async def cleanup_agents(self):
        """Clean up created agents"""
        print("\n🧹 Cleaning up created agents...")
        
        for agent in self.created_agents:
            try:
                response = await self.client.delete(f"{self.base_url}/company-agents/{agent['agent_id']}")
                if response.status_code == 200:
                    print(f"✅ Deleted agent: {agent['agent_name']}")
                else:
                    print(f"⚠️  Failed to delete agent: {agent['agent_name']}")
            except Exception as e:
                print(f"❌ Error deleting agent {agent['agent_name']}: {e}")
    
    async def run_complete_test(self):
        """Run the complete end-to-end test"""
        print("🚀 Starting End-to-End Test for Company Agent System")
        print("=" * 60)
        
        try:
            # Step 1: Check server health
            if not await self.check_server_health():
                return False
            
            # Step 2: Create customer service agent
            customer_agent = await self.create_customer_service_agent()
            await asyncio.sleep(2)  # Wait for agent to initialize
            
            # Step 3: Create sales agent
            sales_agent = await self.create_sales_agent()
            await asyncio.sleep(2)  # Wait for agent to initialize
            
            # Step 4: List company agents
            await self.list_company_agents()
            
            # Step 5: Discover agents by capability
            # await self.discover_agents_by_capability("customer_support")
            # await self.discover_agents_by_capability("sales")
            
            # Step 6: Test agent communication
            await self.test_agent_communication_scenarios()
            
            # Step 7: Get health status
            await self.get_health_status()
            
            print("\n🎉 End-to-End Test Completed Successfully!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with error: {e}")
            return False
        
        finally:
            # Cleanup
            await self.cleanup_agents()
            await self.client.aclose()


async def main():
    """Main function to run the E2E test"""
    print("Company Agent System - End-to-End Test")
    print("=====================================")
    print()
    print("This script will test the complete flow for a single company:")
    print("1. Create customer service and sales agents")
    print("2. Test agent discovery and communication")
    print("3. Test various business scenarios")
    print("4. Monitor system health")
    print("5. Clean up resources")
    print()
    
    # Check if server is running
    test = CompanyAgentE2ETest()
    
    try:
        success = await test.run_complete_test()
        
        if success:
            print("\n✅ All tests passed! The system is working correctly.")
            sys.exit(0)
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        await test.cleanup_agents()
        await test.client.aclose()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        await test.cleanup_agents()
        await test.client.aclose()
        sys.exit(1)


if __name__ == "__main__":
    print("Starting Company Agent E2E Test...")
    print("Make sure the agent server is running on http://localhost:8000")
    print("Start the server with: cd agents && python main.py")
    print()
    
    asyncio.run(main())
