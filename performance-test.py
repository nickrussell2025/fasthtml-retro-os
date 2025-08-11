import requests
import time
import threading
import statistics
import psutil
import os
import gc
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter

class RetroOSPerformanceAnalyzer:
    def __init__(self, base_url="http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results = []
        
    def get_memory_breakdown(self):
        """Analyze current process memory in detail"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        # Object analysis
        objects_by_type = Counter(type(obj).__name__ for obj in gc.get_objects())
        
        # Large objects
        large_objects = []
        for obj in gc.get_objects():
            try:
                size = sys.getsizeof(obj)
                if size > 1024:  # Objects > 1KB
                    large_objects.append((type(obj).__name__, size))
            except:
                pass
        large_objects.sort(key=lambda x: x[1], reverse=True)
        
        # Heavy modules
        heavy_modules = []
        data_science_modules = ['numpy', 'pandas', 'matplotlib', 'scipy', 'torch', 'tensorflow', 'sklearn']
        for name in sys.modules:
            if any(heavy in name.lower() for heavy in data_science_modules):
                heavy_modules.append(name)
        
        return {
            "rss_mb": round(memory_info.rss / 1024 / 1024, 2),
            "vms_mb": round(memory_info.vms / 1024 / 1024, 2),
            "percent": round(process.memory_percent(), 2),
            "python_objects": len(gc.get_objects()),
            "threads": process.num_threads(),
            "modules": len(sys.modules),
            "top_objects": objects_by_type.most_common(10),
            "large_objects": large_objects[:8],
            "heavy_modules": heavy_modules
        }
    
    def memory_test_server(self):
        """Test server's memory endpoint"""
        try:
            response = requests.get(f"{self.base_url}/debug/memory")
            if response.status_code == 200:
                return {"server_accessible": True, "debug_endpoint": "working"}
            else:
                return {"server_accessible": False, "status": response.status_code}
        except Exception as e:
            return {"server_accessible": False, "error": str(e)}
    
    def single_request(self, endpoint, method="GET", data=None):
        """Single request with timing"""
        start_time = time.time()
        try:
            if method == "GET":
                response = requests.get(f"{self.base_url}{endpoint}")
            else:
                response = requests.post(f"{self.base_url}{endpoint}", data=data)
            
            end_time = time.time()
            return {
                "endpoint": endpoint,
                "status": response.status_code,
                "response_time": (end_time - start_time) * 1000,  # ms
                "success": response.status_code == 200,
                "size_bytes": len(response.content)
            }
        except Exception as e:
            return {
                "endpoint": endpoint,
                "status": 0,
                "response_time": 0,
                "success": False,
                "error": str(e)
            }
    
    def simulate_user_session(self, user_id):
        """Simulate realistic user interaction"""
        session_results = []
        
        endpoints = [
            ("/", "GET"),
            ("/open", "POST", {"name": "Game of Life", "type": "program", "icon_x": 1, "icon_y": 1}),
            ("/gameoflife/random", "POST"),
            ("/gameoflife/step", "POST"),
            ("/gameoflife/step", "POST"),
            ("/gameoflife/toggle/5/5", "POST"),
            ("/open", "POST", {"name": "eReader", "type": "program", "icon_x": 2, "icon_y": 1}),
            ("/open", "POST", {"name": "Settings", "type": "program", "icon_x": 3, "icon_y": 1}),
        ]
        
        for endpoint_data in endpoints:
            if len(endpoint_data) == 3:
                endpoint, method, data = endpoint_data
            else:
                endpoint, method = endpoint_data
                data = None
                
            result = self.single_request(endpoint, method, data)
            result["user_id"] = user_id
            session_results.append(result)
            
            time.sleep(0.05 + (user_id * 0.01))  # Stagger users
            
        return session_results
    
    def load_test_with_memory(self, concurrent_users=10, iterations=1):
        """Load test with memory monitoring"""
        print(f"🚀 Starting load test with memory monitoring...")
        print(f"   Users: {concurrent_users}, Iterations: {iterations}")
        
        # Initial memory snapshot
        initial_memory = self.get_memory_breakdown()
        
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            
            for iteration in range(iterations):
                for user_id in range(concurrent_users):
                    future = executor.submit(self.simulate_user_session, user_id)
                    futures.append(future)
            
            # Collect results
            all_results = []
            for future in as_completed(futures):
                session_results = future.result()
                all_results.extend(session_results)
        
        # Final memory snapshot
        final_memory = self.get_memory_breakdown()
        
        # Force garbage collection
        gc_before = len(gc.get_objects())
        collected = gc.collect()
        gc_after = len(gc.get_objects())
        
        # Post-GC memory
        post_gc_memory = self.get_memory_breakdown()
        
        return {
            "performance": self.analyze_results(all_results),
            "memory_analysis": {
                "initial": initial_memory,
                "final": final_memory,
                "post_gc": post_gc_memory,
                "gc_collected": collected,
                "gc_freed": gc_before - gc_after
            }
        }
    
    def analyze_results(self, results):
        """Analyze performance results"""
        successful_results = [r for r in results if r["success"]]
        response_times = [r["response_time"] for r in successful_results]
        
        if not response_times:
            return {"error": "No successful requests"}
        
        return {
            "total_requests": len(results),
            "successful_requests": len(successful_results),
            "success_rate": len(successful_results) / len(results) * 100,
            "avg_response_time": statistics.mean(response_times),
            "median_response_time": statistics.median(response_times),
            "p95_response_time": sorted(response_times)[int(len(response_times) * 0.95)],
            "max_response_time": max(response_times),
            "min_response_time": min(response_times),
            "total_data_transferred": sum(r.get("size_bytes", 0) for r in successful_results)
        }
    
    def run_comprehensive_analysis(self):
        """Run full performance and memory analysis"""
        print("=" * 80)
        print("🔬 RETRO OS COMPREHENSIVE ANALYSIS")
        print("=" * 80)
        
        # Check server connectivity
        server_check = self.memory_test_server()
        if not server_check.get("server_accessible"):
            print("❌ Server not accessible! Start your FastHTML app first.")
            return
        
        print("✅ Server accessible")
        
        # Initial system state
        print("\n📊 Initial Memory Analysis")
        initial_state = self.get_memory_breakdown()
        self.print_memory_analysis(initial_state, "BASELINE")
        
        # Performance tests with increasing load
        test_scenarios = [
            (1, 1, "Single User Baseline"),
            (5, 1, "Light Load"),
            (15, 1, "Medium Load"),
            (30, 1, "Heavy Load")
        ]
        
        for users, iterations, description in test_scenarios:
            print(f"\n🎯 {description} ({users} users)")
            print("-" * 50)
            
            results = self.load_test_with_memory(users, iterations)
            
            # Performance results
            perf = results["performance"]
            print(f"  Success Rate: {perf['success_rate']:.1f}%")
            print(f"  Avg Response: {perf['avg_response_time']:.1f}ms")
            print(f"  P95 Response: {perf['p95_response_time']:.1f}ms")
            print(f"  Max Response: {perf['max_response_time']:.1f}ms")
            
            # Memory impact
            mem = results["memory_analysis"]
            memory_delta = mem["final"]["rss_mb"] - mem["initial"]["rss_mb"]
            objects_delta = mem["final"]["python_objects"] - mem["initial"]["python_objects"]
            
            print(f"  Memory Delta: {memory_delta:+.2f} MB")
            print(f"  Objects Delta: {objects_delta:+,}")
            print(f"  GC Freed: {mem['gc_freed']:,} objects")
            
            # Memory efficiency per user
            if users > 0:
                memory_per_user = memory_delta / users if memory_delta > 0 else 0
                print(f"  Memory/User: {memory_per_user:.3f} MB")
        
        print("\n" + "=" * 80)
        print("🏆 OPTIMIZATION RECOMMENDATIONS")
        print("=" * 80)
        
        # Analyze for optimization opportunities
        final_state = self.get_memory_breakdown()
        self.print_optimization_recommendations(final_state)
    
    def print_memory_analysis(self, memory_data, label):
        """Print detailed memory analysis"""
        print(f"\n  📈 {label} MEMORY BREAKDOWN:")
        print(f"    Physical RAM: {memory_data['rss_mb']} MB")
        print(f"    Virtual RAM:  {memory_data['vms_mb']} MB")
        print(f"    Objects:      {memory_data['python_objects']:,}")
        print(f"    Modules:      {memory_data['modules']}")
        print(f"    Threads:      {memory_data['threads']}")
        
        print(f"\n  🏗️ Top Object Types:")
        for obj_type, count in memory_data['top_objects'][:5]:
            print(f"    {obj_type}: {count:,}")
        
        if memory_data['heavy_modules']:
            print(f"\n  🐘 Heavy Modules Detected:")
            for module in memory_data['heavy_modules']:
                print(f"    ⚠️  {module}")
    
    def print_optimization_recommendations(self, memory_data):
        """Print optimization recommendations"""
        rss_mb = memory_data['rss_mb']
        modules = memory_data['modules']
        heavy_modules = memory_data['heavy_modules']
        
        print(f"\n💡 MEMORY OPTIMIZATION OPPORTUNITIES:")
        
        if rss_mb > 60:
            print(f"  🔸 High memory usage ({rss_mb} MB) - investigate large objects")
        elif rss_mb < 40:
            print(f"  ✅ Excellent memory efficiency ({rss_mb} MB)")
        else:
            print(f"  ✅ Good memory efficiency ({rss_mb} MB)")
        
        if modules > 400:
            print(f"  🔸 Many modules loaded ({modules}) - consider lazy imports")
        else:
            print(f"  ✅ Reasonable module count ({modules})")
        
        if heavy_modules:
            print(f"  ⚠️  Heavy modules detected - consider removing:")
            for module in heavy_modules[:3]:
                print(f"     • {module}")
        else:
            print(f"  ✅ No heavy data science modules detected")
        
        # Scaling projection
        memory_per_100_users = rss_mb + (rss_mb * 0.02)  # Estimate 2% growth per 100 users
        print(f"\n📊 SCALING PROJECTION:")
        print(f"  Current baseline: {rss_mb} MB")
        print(f"  Projected for 100 users: {memory_per_100_users:.1f} MB")
        
        if memory_per_100_users < 100:
            print(f"  🏆 Excellent scalability for target load")
        elif memory_per_100_users < 200:
            print(f"  ✅ Good scalability for target load")
        else:
            print(f"  ⚠️  May need optimization for 100+ users")

def main():
    """Run the comprehensive analysis"""
    analyzer = RetroOSPerformanceAnalyzer()
    analyzer.run_comprehensive_analysis()

if __name__ == "__main__":
    main()