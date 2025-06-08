#!/usr/bin/env python3
"""
Simple test to verify the MCP Git server is working correctly.
This sends actual MCP JSON-RPC messages to test the server.
"""

import asyncio
import json
import subprocess
import sys
import tempfile
import os
from pathlib import Path

async def test_mcp_server():
    print("🧪 Testing MCP Git Server...")
    
    # Create a temporary git repo for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        test_repo = Path(temp_dir) / "test_repo"
        test_repo.mkdir()
        
        # Initialize git repo
        subprocess.run(["git", "init"], cwd=test_repo, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=test_repo)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=test_repo)
        
        # Create a test file
        (test_repo / "test.txt").write_text("Hello, MCP!")
        
        print(f"✓ Created test repo at: {test_repo}")
        
        # Start the MCP server process
        cmd = [sys.executable, "-m", "mcp_server_git"]
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )
        
        try:
            # Test 1: Initialize
            init_msg = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {}
                    },
                    "clientInfo": {
                        "name": "test-client",
                        "version": "1.0.0"
                    }
                }
            }
            
            print("📤 Sending initialize message...")
            process.stdin.write(json.dumps(init_msg) + "\n")
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                if response.get("result"):
                    print("✅ Server initialized successfully!")
                else:
                    print(f"❌ Initialization failed: {response}")
                    return False
            else:
                print("❌ No response from server")
                return False
            
            # Test 2: List tools
            list_tools_msg = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list"
            }
            
            print("📤 Requesting tools list...")
            process.stdin.write(json.dumps(list_tools_msg) + "\n")
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                tools = response.get("result", {}).get("tools", [])
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool['description']}")
                
                expected_tools = ["git_status", "git_add", "git_commit", "git_init"]
                found_tools = [tool["name"] for tool in tools]
                
                for expected in expected_tools:
                    if expected in found_tools:
                        print(f"   ✓ {expected}")
                    else:
                        print(f"   ❌ Missing {expected}")
                        return False
                        
            else:
                print("❌ No response to tools/list")
                return False
            
            # Test 3: Call git_status tool
            status_msg = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {
                    "name": "git_status",
                    "arguments": {
                        "repo_path": str(test_repo)
                    }
                }
            }
            
            print("📤 Testing git_status tool...")
            process.stdin.write(json.dumps(status_msg) + "\n")
            process.stdin.flush()
            
            response_line = process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    content = response["result"]["content"][0]["text"]
                    print("✅ git_status worked!")
                    print(f"   Status: {content[:100]}...")
                else:
                    print(f"❌ git_status failed: {response}")
                    return False
            else:
                print("❌ No response to git_status")
                return False
            
            print("\n🎉 MCP Git Server is working correctly!")
            return True
            
        except Exception as e:
            print(f"❌ Error testing server: {e}")
            return False
            
        finally:
            # Clean up
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                process.kill()

if __name__ == "__main__":
    success = asyncio.run(test_mcp_server())
    sys.exit(0 if success else 1)
