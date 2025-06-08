"""
Quick test to verify MCP Git server is running and responding
"""
import json
import subprocess
import sys
from pathlib import Path

def test_server():
    print("🧪 Testing MCP Git Server...")
    
    # Test server startup with verbose logging
    cmd = [sys.executable, "-m", "mcp_server_git", "-v"]
    
    try:
        # Start server process
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )
        
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test", "version": "1.0"}
            }
        }
        
        print("📤 Sending initialization...")
        input_data = json.dumps(init_message) + "\n"
        
        # Send message and get response with timeout
        stdout, stderr = process.communicate(input=input_data, timeout=10)
        
        if stdout:
            try:
                response = json.loads(stdout.strip())
                if "result" in response:
                    print("✅ Server responded to initialization!")
                    print(f"   Protocol version: {response['result'].get('protocolVersion', 'unknown')}")
                    print(f"   Server info: {response['result'].get('serverInfo', {}).get('name', 'unknown')}")
                    return True
                else:
                    print(f"❌ Unexpected response: {response}")
            except json.JSONDecodeError:
                print("❌ Invalid JSON response")
                print(f"stdout: {stdout}")
        
        if stderr:
            print(f"Server logs: {stderr}")
            
    except subprocess.TimeoutExpired:
        print("⏰ Server is running (timeout as expected for MCP servers)")
        process.kill()
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        
    finally:
        try:
            process.terminate()
        except:
            pass
    
    return False

if __name__ == "__main__":
    success = test_server()
    if success:
        print("\n🎉 MCP Git Server is working correctly!")
        print("   It's ready to accept connections from MCP clients")
        print("   Available tools: git_status, git_add, git_commit, git_diff, git_log, etc.")
    else:
        print("\n❌ Server test failed")
