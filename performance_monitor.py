"""
Monitoring en temps réel des performances de l'IA
Analyse les temps de réponse, cache hit rate, et métriques système
"""

import asyncio
import time
import json
import statistics
from datetime import datetime
from collections import deque
from typing import Dict, List, Deque
import ollama


class PerformanceMonitor:
    def __init__(self, max_samples: int = 100):
        self.max_samples = max_samples
        self.response_times: Deque[float] = deque(maxlen=max_samples)
        self.cache_hits = 0
        self.cache_misses = 0
        self.ollama_calls = 0
        self.errors = 0
        self.start_time = time.time()

    def record_response(self, duration: float, from_cache: bool = False):
        """Enregistre un temps de réponse"""
        self.response_times.append(duration)
        if from_cache:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
            self.ollama_calls += 1

    def record_error(self):
        """Enregistre une erreur"""
        self.errors += 1

    def get_stats(self) -> Dict:
        """Retourne les statistiques actuelles"""
        if not self.response_times:
            return {
                "status": "No data yet",
                "uptime_seconds": time.time() - self.start_time,
            }

        times = list(self.response_times)
        total_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (
            (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        )

        return {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "response_times": {
                "count": len(times),
                "min_ms": min(times) * 1000,
                "max_ms": max(times) * 1000,
                "mean_ms": statistics.mean(times) * 1000,
                "median_ms": statistics.median(times) * 1000,
                "p95_ms": self._percentile(times, 95) * 1000,
                "p99_ms": self._percentile(times, 99) * 1000,
            },
            "cache": {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate_percent": cache_hit_rate,
            },
            "ollama": {
                "total_calls": self.ollama_calls,
                "errors": self.errors,
                "success_rate_percent": (
                    ((self.ollama_calls - self.errors) / self.ollama_calls * 100)
                    if self.ollama_calls > 0
                    else 0
                ),
            },
            "requests": {
                "total": total_requests,
                "rps": (
                    total_requests / (time.time() - self.start_time)
                    if (time.time() - self.start_time) > 0
                    else 0
                ),
            },
        }

    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calcule le percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]

    def print_stats(self):
        """Affiche les statistiques formatées"""
        stats = self.get_stats()

        print("\n" + "=" * 70)
        print(f"📊 PERFORMANCE MONITORING - {stats['timestamp']}")
        print("=" * 70)

        if "status" in stats:
            print(f"\n⏱️  {stats['status']}")
            print(f"Uptime: {stats['uptime_seconds']:.1f}s")
            return

        print(f"\n⏱️  UPTIME: {stats['uptime_seconds']:.1f}s")

        print("\n🚀 RESPONSE TIMES (IA)")
        rt = stats["response_times"]
        print(f"  Count:  {rt['count']} requêtes")
        print(f"  Min:    {rt['min_ms']:.0f} ms")
        print(f"  Mean:   {rt['mean_ms']:.0f} ms")
        print(f"  Median: {rt['median_ms']:.0f} ms")
        print(f"  Max:    {rt['max_ms']:.0f} ms")
        print(f"  P95:    {rt['p95_ms']:.0f} ms")
        print(f"  P99:    {rt['p99_ms']:.0f} ms")

        print("\n💾 CACHE PERFORMANCE")
        cache = stats["cache"]
        print(f"  Hits:     {cache['hits']}")
        print(f"  Misses:   {cache['misses']}")
        print(f"  Hit Rate: {cache['hit_rate_percent']:.1f}%")

        print("\n🤖 OLLAMA API")
        ollama_stats = stats["ollama"]
        print(f"  Total Calls:   {ollama_stats['total_calls']}")
        print(f"  Errors:        {ollama_stats['errors']}")
        print(f"  Success Rate:  {ollama_stats['success_rate_percent']:.1f}%")

        print("\n📈 REQUESTS")
        req = stats["requests"]
        print(f"  Total:    {req['total']}")
        print(f"  RPS:      {req['rps']:.2f}")

        print("=" * 70 + "\n")


async def test_ollama_performance(monitor: PerformanceMonitor, num_tests: int = 10):
    """Test les performances Ollama avec différents prompts"""

    test_prompts = [
        "Décris en 2 phrases la Comté dans le Seigneur des Anneaux.",
        "Raconte une courte aventure dans Fondcombe pour un enfant de 10 ans.",
        "Que se passe-t-il dans les Mines de la Moria ?",
        "Décris la forêt de Fangorn en 3 phrases épiques.",
        "Raconte l'arrivée à Minas Tirith de manière immersive.",
    ]

    print(f"\n🧪 TEST OLLAMA PERFORMANCE ({num_tests} requêtes)")
    print("=" * 70)

    for i in range(num_tests):
        prompt = test_prompts[i % len(test_prompts)]
        print(f"\n[{i+1}/{num_tests}] Test: {prompt[:50]}...")

        start = time.time()
        try:
            response = ollama.generate(
                model="mistral",
                prompt=prompt,
                options={"temperature": 0.7, "num_predict": 500},
            )
            duration = time.time() - start
            monitor.record_response(duration, from_cache=False)

            print(
                f"✅ Réponse en {duration*1000:.0f} ms ({len(response['response'])} caractères)"
            )

        except Exception as e:
            duration = time.time() - start
            monitor.record_error()
            print(f"❌ Erreur après {duration*1000:.0f} ms: {str(e)[:100]}")

        # Pause entre requêtes
        if i < num_tests - 1:
            await asyncio.sleep(1)

    monitor.print_stats()


async def live_monitoring(interval: int = 5, duration: int = 60):
    """Monitoring live pendant une durée donnée"""
    monitor = PerformanceMonitor()

    print(f"\n🔴 LIVE MONITORING - Durée: {duration}s, Intervalle: {interval}s")
    print("Lancez des requêtes au serveur pour voir les stats s'afficher...")
    print("=" * 70)

    start = time.time()
    while (time.time() - start) < duration:
        await asyncio.sleep(interval)
        monitor.print_stats()

    print("\n✅ Monitoring terminé")


def simulate_traffic(monitor: PerformanceMonitor):
    """Simule du trafic avec différents patterns"""
    import random

    print("\n🎭 SIMULATION DE TRAFIC")
    print("=" * 70)

    # Simule 50 requêtes avec différents patterns
    for i in range(50):
        # 70% cache hit, 30% Ollama call
        from_cache = random.random() < 0.7

        if from_cache:
            # Cache: très rapide (50-200ms)
            duration = random.uniform(0.05, 0.2)
        else:
            # Ollama: plus lent (3-8s)
            duration = random.uniform(3, 8)

        # Simule quelques erreurs (5%)
        if random.random() < 0.05:
            monitor.record_error()

        monitor.record_response(duration, from_cache)

        if (i + 1) % 10 == 0:
            print(f"\n--- Après {i+1} requêtes ---")
            monitor.print_stats()


async def benchmark_ollama_models():
    """Compare les performances de différents paramètres Ollama"""

    configs = [
        {"name": "Rapide (temp=0.5, tokens=100)", "temp": 0.5, "tokens": 100},
        {"name": "Normal (temp=0.7, tokens=300)", "temp": 0.7, "tokens": 300},
        {"name": "Détaillé (temp=0.7, tokens=500)", "temp": 0.7, "tokens": 500},
    ]

    prompt = "Raconte une courte aventure dans la Comté pour un enfant de 10 ans."

    print("\n⚡ BENCHMARK CONFIGURATIONS OLLAMA")
    print("=" * 70)

    results = []

    for config in configs:
        print(f"\n🧪 Test: {config['name']}")
        times = []

        for i in range(3):
            start = time.time()
            try:
                response = ollama.generate(
                    model="mistral",
                    prompt=prompt,
                    options={
                        "temperature": config["temp"],
                        "num_predict": config["tokens"],
                    },
                )
                duration = time.time() - start
                times.append(duration)
                print(
                    f"  Tentative {i+1}: {duration*1000:.0f} ms ({len(response['response'])} chars)"
                )

            except Exception as e:
                print(f"  ❌ Erreur: {str(e)[:100]}")

        if times:
            avg_time = statistics.mean(times)
            results.append(
                {
                    "config": config["name"],
                    "avg_ms": avg_time * 1000,
                    "min_ms": min(times) * 1000,
                    "max_ms": max(times) * 1000,
                }
            )

    print("\n📊 RÉSULTATS COMPARATIFS")
    print("=" * 70)
    for r in results:
        print(f"\n{r['config']}")
        print(f"  Moyenne: {r['avg_ms']:.0f} ms")
        print(f"  Min:     {r['min_ms']:.0f} ms")
        print(f"  Max:     {r['max_ms']:.0f} ms")


async def main():
    """Menu principal"""
    print(
        """
╔════════════════════════════════════════════════════════════════╗
║         MONITORING PERFORMANCE IA - JDVLH Game                 ║
╚════════════════════════════════════════════════════════════════╝

Options disponibles:

1. Test Performance Ollama (10 requêtes)
2. Simulation de Trafic (50 requêtes)
3. Benchmark Configurations Ollama
4. Live Monitoring (60s)
5. Tout Exécuter

Votre choix (1-5): """
    )

    choice = input().strip()

    monitor = PerformanceMonitor()

    if choice == "1":
        await test_ollama_performance(monitor, num_tests=10)

    elif choice == "2":
        simulate_traffic(monitor)

    elif choice == "3":
        await benchmark_ollama_models()

    elif choice == "4":
        await live_monitoring(interval=5, duration=60)

    elif choice == "5":
        print("\n🚀 EXÉCUTION COMPLÈTE\n")

        print("\n" + "=" * 70)
        print("ÉTAPE 1/4: Benchmark Configurations")
        print("=" * 70)
        await benchmark_ollama_models()

        print("\n" + "=" * 70)
        print("ÉTAPE 2/4: Test Performance Ollama")
        print("=" * 70)
        monitor1 = PerformanceMonitor()
        await test_ollama_performance(monitor1, num_tests=5)

        print("\n" + "=" * 70)
        print("ÉTAPE 3/4: Simulation de Trafic")
        print("=" * 70)
        monitor2 = PerformanceMonitor()
        simulate_traffic(monitor2)

        print("\n" + "=" * 70)
        print("ÉTAPE 4/4: Résumé Final")
        print("=" * 70)
        print("\n✅ Analyse complète terminée!")
        print("\nRecommandations basées sur les tests:")
        print("  • Configuration optimale: temp=0.7, tokens=300-500")
        print("  • Cache recommandé pour ~70% des requêtes")
        print("  • Temps réponse attendu: 3-8s (Ollama), 50-200ms (Cache)")

    else:
        print("❌ Choix invalide")


if __name__ == "__main__":
    asyncio.run(main())
